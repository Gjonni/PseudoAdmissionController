import kubernetes
from openshift.dynamic import DynamicClient
import urllib3
import os
import _thread
# from library.ValidationEnviroment import ValidationEnviroment, conv_memory_to_bytes, add_attribute, conv_core_to_millicore
from library.ValidationEnviroment import *
from library.Logging import Logging



### Funziona su Openshift or Kubernetes
urllib3.disable_warnings()


if "OPENSHIFT_BUILD_NAME" in os.environ:
    kubernetes.config.load_incluster_config()
    file_namespace = open("/run/secrets/kubernetes.io/serviceaccount/namespace", "r")
    if file_namespace.mode == "r":
        namespace = file_namespace.read()
        print(f"namespace: { namespace }")
else:
    kubernetes.config.load_kube_config()
    namespace = "op-test"


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
    Logging.logger.debug(f"IN OCP for Kind: {kind}")

    # Set TARGET Range for Request and Limit of CPU and Memory.
    Logging.logger.debug(f"Kind: {kind} ------------------- START Set TARGET Range for Request and Limit of CPU and Memory ------------------------")
    requestMemory = ValidationEnviroment().requestMemory
    requestCpu = ValidationEnviroment().requestCpu
    limitsMemory = ValidationEnviroment().limitsMemory
    limitsCpu = ValidationEnviroment().limitsCpu

    Logging.logger.debug(f"Kind: {kind} - SETTED RANGE:")
    Logging.logger.debug(f"Kind: {kind}     - requestMemory: {requestMemory}")
    Logging.logger.debug(f"Kind: {kind}     - requestCpu: {requestCpu}")
    Logging.logger.debug(f"Kind: {kind}     - limitsMemory: {limitsMemory}")
    Logging.logger.debug(f"Kind: {kind}     - limitsCpu: {limitsCpu}")

    Logging.logger.debug(f"Kind: {kind} ------------------- END TARGET Range INFO ------------------------")

    for object in v1_ocp.watch(namespace=namespace):
        if not (
            object["object"].metadata.namespace in ValidationEnviroment().namespaces
            and object["object"].metadata.name not in ValidationEnviroment().excludeObject
        ):
            continue
        if object["type"] not in ["ADDED", "MODIFIED"]:
            continue

        for container in object["object"].spec.template.spec.containers:
            Logging.logger.debug(f"Kind: {kind} ------------------- START CONTAINER INFO ------------------------")
            Logging.logger.debug(f"Kind: {kind} - CONTAINER {container.name} request: {container.resources.requests}")
            Logging.logger.debug(f"Kind: {kind} - CONTAINER {container.name} limits: {container.resources.limits}")
            Logging.logger.debug(f"Kind: {kind} ------------------- END CONTAINER INFO --------------------------")


            # Check REQUESTS
            # Exchange Memory and CPU REQUEST at: null with: 0
            if  not container.resources.requests:
                container.resources.requests = add_attribute({"memory": 0,"cpu": 0})

            # Convert Memory to Bytes and CPU: Millicore
            container.resources.requests.memory = conv_memory_to_bytes(container.resources.requests.memory)
            container.resources.requests.cpu = conv_core_to_millicore(container.resources.requests.cpu)

            # Check MEMORY REQUEST
            if ( container.resources.requests.memory < requestMemory.min
                or container.resources.requests.memory > requestMemory.max):
                Logging.logger.info(f"{ ThreadName } -- MEMORY REQUEST -- Policy Violation for: { kind } { object['object'].metadata.name } --> Container: { container.name } - Actual Memory Requests: { container.resources.requests.memory} in Namespace: { object['object'].metadata.namespace } - Scale to 0 ")
                scale_down(object["object"].kind, object["object"].metadata.name, object["object"].metadata.namespace,)

            # Check CPU REQUEST
            if ( container.resources.requests.cpu < requestCpu.min
                or container.resources.requests.cpu > requestCpu.max):
                Logging.logger.info(f"{ ThreadName } -- CPU REQUEST -- Policy Violation for: { kind } { object['object'].metadata.name } --> Container: { container.name } - Actual CPU Requests: { container.resources.requests.cpu} in Namespace: { object['object'].metadata.namespace } - Scale to 0 ")
                scale_down(object["object"].kind, object["object"].metadata.name, object["object"].metadata.namespace,)


            # Check LIMITS
            # Exchange Memory and CPU LIMIT at: null with: 0
            if  not container.resources.limits:
                container.resources.limits = add_attribute({"memory": "0","cpu": "0"})

            # Convert Memory to Bytes and CPU: Millicore
            container.resources.limits.memory = conv_memory_to_bytes(container.resources.limits.memory)
            container.resources.limits.cpu = conv_core_to_millicore(container.resources.limits.cpu)

            # Check MEMORY LIMIT
            if ( container.resources.limits.memory < limitsMemory.min
                or container.resources.limits.memory > limitsMemory.max):
                Logging.logger.info(f"{ ThreadName } --  MEMORY LIMIT -- Policy Violation for: { kind } { object['object'].metadata.name } --> Container: { container.name } - Actual Memory limit: { container.resources.limits.memory} in Namespace: { object['object'].metadata.namespace } - Scale to 0 ")
                scale_down(object["object"].kind, object["object"].metadata.name, object["object"].metadata.namespace,)


            # Check CPU LIMIT
            if ( container.resources.limits.cpu < limitsCpu.min
                or container.resources.limits.cpu > limitsCpu.max):
                Logging.logger.info(f"{ ThreadName } --  CPU LIMIT -- Policy Violation for: { kind } { object['object'].metadata.name } --> Container: { container.name } - Actual CPU limit: { container.resources.limits.memory} in Namespace: { object['object'].metadata.namespace } - Scale to 0 ")
                scale_down(object["object"].kind, object["object"].metadata.name, object["object"].metadata.namespace,)



def main():
    _thread.start_new_thread(ocp, ("DeploymentConfig-Thread", 2, "DeploymentConfig"))
    _thread.start_new_thread(ocp, ("Deployment-Thread", 4, "Deployment"))

    while 1:
        pass


if __name__ == "__main__":
    main()
