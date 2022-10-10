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

##### LOGGING
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=os.environ.get("LOGLEVEL", "DEBUG"))
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
    namespace = 'passbolt'

    
k8s_client = kubernetes.client.ApiClient()
dyn_client = DynamicClient(k8s_client)


def validation_resources():
    if "REQUEST_MEMORY" not in os.environ :
        logger.debug(f"Failed because REQUEST_MEMORY  is not set.")
        raise EnvironmentError(f"Failed because REQUEST_MEMORY is not set.")
    return { 'requests': {'memory': list((os.environ.get("REQUEST_MEMORY"),)),'cpu': [] },'limits': {'memory': ['512Mi','2Gi'],'cpu': [] } }

def validation_namespace():
    if "NAMESPACES" not in os.environ:
        logger.debug("Failed because NAMESPACES is not set.")
        raise EnvironmentError("Failed because NAMESPACES is not set.")
    return list((os.environ.get("NAMESPACES",'passbolt'),))

def validation_exclude():
    if "EXCLUDE" not in os.environ:
        logger.debug("Failed because EXCLUDE is not set.")
        raise EnvironmentError("Failed because NAMESPACES is not set.")
    return list((os.environ.get("EXCLUDE",'test-d'),))


def scale_down(kind,name,namespace):
    resources = dyn_client.resources.get(api_version="v1", kind=kind)
    body = {
        'kind': kind,
        'apiVersion': 'v1',
        'metadata': {'name': name },
        'spec': {
            'replicas': 0,
        }
    }
    resources.patch(body=body, namespace=namespace)


def ocp(kind):
    v1_ocp = dyn_client.resources.get(api_version="v1", kind=kind)
    for object in v1_ocp.watch(namespace=namespace):
        if object['object'].metadata.namespace in validation_namespace() and object['object'].metadata.name not in validation_exclude() :
            if object['type'] == "ADDED" or object['type'] == "MODIFIED": 
                for container in object['object'].spec.template.spec.containers:
                        if container.resources:
                            if container.resources.requests and container.resources.requests.memory and container.resources.requests.memory not in validation_resources()['requests']['memory']:
                                logger.debug(f"Policy Violation from Container { container.name } - nella { kind } { object['object'].metadata.name } - { container.resources.requests.memory } in namespace { object['object'].metadata.namespace } - Scale to 0 ")
                                scale_down( object['object'].kind , object['object'].metadata.name, object['object'].metadata.namespace)
                            
                            if container.resources.limits and container.resources.limits.memory and container.resources.limits.memory not in validation_resources()['limits']['memory'] :
                                logger.debug(f"Policy Violation from Container { container.name } - nella { kind } { object['object'].metadata.name } - { container.resources.limits.memory } in namespace { object['object'].metadata.namespace } - Scale to 0 ")
                                scale_down( object['object'].kind , object['object'].metadata.name, object['object'].metadata.namespace)



def main():
    with ThreadPoolExecutor(max_workers=4) as e:
        e.submit(ocp,"DeploymentConfig")
        e.submit(ocp,"Deployment")
        e.shutdown(wait=True, cancel_futures=False)

 #   _thread.start_new_thread( ocp, ("DeploymentConfig-Thread", 2, "DeploymentConfig" ) )
 #   _thread.start_new_thread( ocp, ("Deployment-Thread", 4, "Deployment" ) ) 
  #  while 1:
  #      pass


if __name__ == "__main__":
    main()
