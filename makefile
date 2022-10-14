SHELL=/bin/bash
### SOLO TESTING NON SO SE FUNGE

NAMESPACE = passbolt
EXCLUDE = passbolt-db
NAME = pseudoadmissioncontroller
TZ = Europe/Rome
LOGLEVEL = INFO
REQUEST_MEMORY = '10Mi,20Mi'
LIMITS_MEMORY = '2Gi,4Gi'
REQUEST_CPU = '100m,200m'
LIMITS_CPU = '2,4'

install:
	@echo "Creazione Immagine request check"
	oc new-app openshift/python:3.9-ubi8~https://github.com/Gjonni/PseudoAdmissionController.git -n $(NAMESPACE)
	oc create  sa $(NAME) -n $(NAMESPACE) 
	oc label sa $(NAME) app=$(NAME) -n $(NAMESPACE)
	@echo "Add Enviroment"
	oc patch deployment $(NAME) -p '{"spec":{"template":{"spec":{"serviceAccount":"pseudoadmissioncontroller"}}}}' -n $(NAMESPACE)
	oc set env deployment/$(NAME) TZ=$(TZ) NAMESPACES=$(NAMESPACE) EXCLUDE=$(EXCLUDE) LOGLEVEL=$(LOGLEVEL) -n $(NAMESPACE) 
	oc set env deployment/$(NAME) REQUEST_MEMORY=$(REQUEST_MEMORY) LIMITS_MEMORY=$(LIMITS_MEMORY) REQUEST_CPU=$(REQUEST_CPU) LIMITS_CPU=$(LIMITS_CPU) -n $(NAMESPACE)
	oc scale deployment/$(NAME) --replicas=1 -n $(NAMESPACE)
	@echo "Fix Permission"
	oc adm policy add-role-to-user admin system:serviceaccount:$(NAMESPACE):$(NAME) -n $(NAMESPACE)



uninstall:
	@echo "Disinstallo Applicazione"
	oc delete all --selector app=$(NAME) -n $(NAMESPACE)
	oc adm policy remove-role-from-user admin system:serviceaccount:$(NAMESPACE):$(NAME) -n $(NAMESPACE)
	oc delete sa $(NAME) -n $(NAMESPACE)
	
