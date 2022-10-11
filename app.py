import kubernetes
from openshift.dynamic import DynamicClient
import urllib3
import os
import logging
import _thread
from library.ValidationEnviroment import ValidationEnviroment
from library.Resources import Resources
from library.Logging import Logging



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
            object["object"].metadata.namespace in ValidationEnviroment().namespaces
            and object["object"].metadata.name not in ValidationEnviroment().excludeObject
        ):
            continue
        if object["type"] not in ["ADDED", "MODIFIED"]:
            continue

        for container in object["object"].spec.template.spec.containers:

            if  not container.resources.requests:
                container.resources.requests = Resources({"memory": "0","cpu": "0"})
            if  not container.resources.requests.memory:
                container.resources.requests.memory = '0'
            if  not container.resources.requests.cpu :
                container.resources.requests.cpu = '0'

            
            if (container.resources.requests.memory not in ValidationEnviroment().requestMemory):
                Logging.logger.info(f"{ThreadName } - Policy Violation from Container { container.name } - nella { kind } { object['object'].metadata.name } - requests ram: { container.resources.requests.memory} in namespace { object['object'].metadata.namespace } - Scale to 0 ")
                scale_down( object["object"].kind, object["object"].metadata.name, object["object"].metadata.namespace,)

            if (container.resources.requests.cpu not in ValidationEnviroment().requestCpu):
                Logging.logger.info(f"{ThreadName } - Policy Violation from Container { container.name } - nella { kind } { object['object'].metadata.name } - requests cpu: { container.resources.requests.cpu} in namespace { object['object'].metadata.namespace } - Scale to 0 ")
                scale_down( object["object"].kind, object["object"].metadata.name, object["object"].metadata.namespace,)


            if  not container.resources.limits:
                container.resources.limits = Resources({"memory": "0","cpu": "0"})
            if  not container.resources.limits.memory:
                container.resources.limits.memory = '0'
            if  not container.resources.limits.cpu :
                container.resources.limits.cpu = '0'

            
            if (container.resources.limits.memory not in ValidationEnviroment().limitsMemory):
                Logging.logger.info(f"{ThreadName } - Policy Violation from Container { container.name } - nella { kind } { object['object'].metadata.name } - limits ram: { container.resources.limits.memory} in namespace { object['object'].metadata.namespace } - Scale to 0 ")
                scale_down( object["object"].kind, object["object"].metadata.name, object["object"].metadata.namespace,)

            if (container.resources.limits.cpu not in ValidationEnviroment().limitsCpu):
                Logging.logger.info(f"{ThreadName } - Policy Violation from Container { container.name } - nella { kind } { object['object'].metadata.name } - limits cpu: { container.resources.limits.cpu} in namespace { object['object'].metadata.namespace } - Scale to 0 ")
                scale_down( object["object"].kind, object["object"].metadata.name, object["object"].metadata.namespace,)



def main():
    _thread.start_new_thread(ocp, ("DeploymentConfig-Thread", 2, "DeploymentConfig"))
    _thread.start_new_thread(ocp, ("Deployment-Thread", 4, "Deployment"))

    while 1:
        pass


if __name__ == "__main__":
    main()
