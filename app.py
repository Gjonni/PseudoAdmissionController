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
    level=os.environ.get("LOGLEVEL", "INFO"),
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
        self.requestMemory = list((os.environ.get("REQUEST_MEMORY"),))
        
    @property
    def requestMemory(self):
        return self._requestMemory

    @requestMemory.setter
    def requestMemory(self, value):
        if not value:
            raise ValueError("Request Memory  is not set.")
        self._requestMemory = value



def validation_resources():
    if "REQUEST_MEMORY" not in os.environ:
        logger.debug(f"Failed because REQUEST_MEMORY  is not set.")
        raise EnvironmentError(f"Failed because REQUEST_MEMORY is not set.")
    return {
        "requests": {"memory": list((os.environ.get("REQUEST_MEMORY"),)), "cpu": []},
        "limits": {"memory": ["512Mi", "2Gi"], "cpu": []},
    }


def validation_namespace():
    if "NAMESPACES" not in os.environ:
        logger.debug("Failed because NAMESPACES is not set.")
        raise EnvironmentError("Failed because NAMESPACES is not set.")
    return list((os.environ.get("NAMESPACES", "passbolt"),))


def validation_exclude():
    if "EXCLUDE" not in os.environ:
        logger.debug("Failed because EXCLUDE is not set.")
        raise EnvironmentError("Failed because EXCLUDE is not set.")
    return list((os.environ.get("EXCLUDE", "test-d"),))


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
            object["object"].metadata.namespace in validation_namespace()
            and object["object"].metadata.name not in validation_exclude()
        ):
            continue
        if object["type"] not in ["ADDED", "MODIFIED"]:
            continue

        for container in object["object"].spec.template.spec.containers:
            if not container.resources.requests:
                container.resources.requests = Resources({"memory": "0"})

            
            logger.debug(f"{container.resources}")
            if (container.resources.requests.memory not in ValidationResources().requestMemory):
                logger.info(f"{ThreadName } - Policy Violation from Container { container.name } - nella { kind } { object['object'].metadata.name } - requests ram: { container.resources.requests} in namespace { object['object'].metadata.namespace } - Scale to 0 ")
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
