import kubernetes
from openshift.dynamic import DynamicClient
import urllib3
import os
import datetime
import time
import logging
import sys
import _thread
from concurrent.futures import ThreadPoolExecutor

# LOGGING
logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=os.environ.get("LOGLEVEL", "DEBUG"),
)
logger = logging.getLogger("route.response.time")

### Openshift or Kubernetes

urllib3.disable_warnings()


if "OPENSHIFT_BUILD_NAME" in os.environ:
    kubernetes.config.load_incluster_config()
    file_namespace = open("/run/secrets/kubernetes.io/serviceaccount/namespace", "r")
    if file_namespace.mode == "r":
        namespace = file_namespace.read()
        print(f"namespace: { namespace }")
else:
    kubernetes.config.load_kube_config()
    namespace = "passbolt"


k8s_client = kubernetes.client.ApiClient()
dyn_client = DynamicClient(k8s_client)


class Resources(dict):
    def __init__(self, dic):
        for key, val in dic.items():
            self.__dict__[key] = self[key] = (
                Resources(val) if isinstance(val, dict) else val
            )


class ValidationResources:
    def __init__(self):
        self.namespaces = os.environ.get("NAMESPACES")
        self.excludeObject = os.environ.get("EXCLUDE")
        self.requestMemory = os.environ.get("REQUEST_MEMORY")
        self.limitsMemory = os.environ.get("LIMITS_MEMORY")

    @property
    def namespaces(self):
        return self._namespaces

    @namespaces.setter
    def namespaces(self, value):
        logger.debug(f"I Namespaces verificati sono {value}")
        if not value:
            raise ValueError("NAMESPACES is not set.")
        self._namespaces = value.split(',')

    @property
    def excludeObject(self):
        return self._excludeObject

    @excludeObject.setter
    def excludeObject(self, value):
        logger.debug(f"Gli oggetti esclusi dalla verifica sono {value}")
        if not value:
            raise ValueError("List Object BlackList is not set.")
        self._excludeObject = value.split(',')

    @property
    def requestMemory(self):
        return self._requestMemory

    @requestMemory.setter
    def requestMemory(self, value):
        logger.debug(f"La whitelist della Request Memory {value}")
        if not value:
            raise ValueError("Limits Memory  is not set.")
        self._requestMemory = value.split(',')

    @property
    def limitsMemory(self):
        return self._limitsMemory

    @limitsMemory.setter
    def limitsMemory(self, value):
        logger.debug(f"La whitelist della Request Memory {value}")
        if not value:
            raise ValueError("Request Memory  is not set.")
        self._limitsMemory = value.split(',')





def scale_down(kind, name, namespace):
    resources = dyn_client.resources.get(api_version="v1", kind=kind)
    body = {
        "kind": kind,
        "apiVersion": "v1",
        "metadata": {"name": name},
        "spec": {
            "replicas": 0,
        },
    }
    resources.patch(body=body, namespace=namespace)


def ocp(ThreadName, delay, kind):
    v1_ocp = dyn_client.resources.get(api_version="v1", kind=kind)

    for object in v1_ocp.watch(namespace=namespace):

        if not (
            object["object"].metadata.namespace in ValidationResources().namespaces
            and object["object"].metadata.name not in ValidationResources().excludeObject
        ):
            continue
        if object["type"] not in ["ADDED", "MODIFIED"]:
            continue

        for container in object["object"].spec.template.spec.containers:

            if  not container.resources.requests:
                container.resources = Resources({"requests":{"memory": "0","cpu": "0"}})
                logger.debug(f"requests: { container.resources}")
            if  not container.resources.requests.memory:
                container.resources.requests.memory = '0'
                logger.debug(f"requests: { container.resources.requests}")
            if  not container.resources.requests.cpu :
                container.resources.requests.cpu = '0'
                logger.debug(f"requests: { container.resources.requests}")

        
            
            if (container.resources.requests.memory not in ValidationResources().requestMemory):
                logger.info(f"{ThreadName } - Policy Violation from Container { container.name } - nella { kind } { object['object'].metadata.name } - requests ram: { container.resources.requests.memory} in namespace { object['object'].metadata.namespace } - Scale to 0 ")
                scale_down( object["object"].kind, object["object"].metadata.name, object["object"].metadata.namespace,)

            if  not container.resources.limits:
                container.resources = Resources({"limits":{"memory": "0","cpu": "0"}})
                logger.debug(f"limits: { container.resources}")
            if  not container.resources.limits:
                container.resources.limits.memory = '0'
                logger.debug(f"limits: { container.resources.limits}")
            if  not container.resources.limits.cpu :
                container.resources.limits.cpu = '0'
                logger.debug(f"limits: { container.resources.limits}")
        
            
            if (container.resources.limits.memory not in ValidationResources().requestMemory):
                logger.info(f"{ThreadName } - Policy Violation from Container { container.name } - nella { kind } { object['object'].metadata.name } - limits ram: { container.resources.limits.memory} in namespace { object['object'].metadata.namespace } - Scale to 0 ")
                scale_down( object["object"].kind, object["object"].metadata.name, object["object"].metadata.namespace,)






def main():
    #    with ThreadPoolExecutor(max_workers=2) as e:
    #        e.submit(ocp, "DeploymentConfig")
    #        e.submit(ocp, "Deployment")
    #        e.shutdown(wait=True, cancel_futures=False)

    _thread.start_new_thread(ocp, ("DeploymentConfig-Thread", 2, "DeploymentConfig"))
    _thread.start_new_thread(ocp, ("Deployment-Thread", 4, "Deployment"))

    while 1:
        pass


if __name__ == "__main__":
    main()
