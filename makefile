SHELL=/bin/bash
### SOLO TESTING NON SO SE FUNGE
### (EN) ONLY TESTING I DON'T KNOW IF IT WORKS

EXCLUDE_OBJECT_NAME = passbolt-db
NAMESPACE = op-test
NAME = pseudoadmissioncontroller
TZ = Europe/Rome
LOGLEVEL = INFO
REQUEST_MEMORY = '10Mi,20Mi'
LIMITS_MEMORY = '500Mi,1Gi,2Gi'
REQUEST_CPU = '100m,200m'
LIMITS_CPU = '500m,1,2'

######################################
####### STOP MODIFIABLE VALUES #######
######################################


install:
	@echo "### Build Image and ServiceAccount"
	oc -n openshift import-image openshift/python:3.9-ubi8 --from=registry.access.redhat.com/ubi8/python-39:1-73.1665597535 --confirm
	oc -n $(NAMESPACE) new-app openshift/python:3.9-ubi8~https://github.com/Gjonni/PseudoAdmissionController.git
	oc -n $(NAMESPACE) create sa $(NAME)
	oc -n $(NAMESPACE) label sa $(NAME) app=$(NAME)
	@echo -e "\n### Add Enviroment"
	oc -n $(NAMESPACE) patch deployment $(NAME) -p '{"spec":{"template":{"spec":{"serviceAccount":"pseudoadmissioncontroller"}}}}'
	oc -n $(NAMESPACE) set env deployment/$(NAME) TZ=$(TZ) NAMESPACES=$(NAMESPACE) EXCLUDE_OBJECT_NAME=$(NAME),$(EXCLUDE_OBJECT_NAME) LOGLEVEL=$(LOGLEVEL)
	oc -n $(NAMESPACE) set env deployment/$(NAME) REQUEST_MEMORY=$(REQUEST_MEMORY) LIMITS_MEMORY=$(LIMITS_MEMORY) REQUEST_CPU=$(REQUEST_CPU) LIMITS_CPU=$(LIMITS_CPU)
	oc -n $(NAMESPACE) scale deployment/$(NAME) --replicas=1
	@echo -e "\n### Fix Permission"
	oc -n $(NAMESPACE) adm policy add-role-to-user admin system:serviceaccount:$(NAMESPACE):$(NAME)


uninstall:
	@echo "### Uninstall Application"
	oc -n $(NAMESPACE) delete all --selector app=$(NAME)
	oc -n $(NAMESPACE) adm policy remove-role-from-user admin system:serviceaccount:$(NAMESPACE):$(NAME)
	oc -n $(NAMESPACE) delete sa $(NAME)
