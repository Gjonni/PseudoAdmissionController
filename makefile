SHELL=/bin/bash
### SOLO TESTING NON SO SE FUNGE
all:
	@echo "make install"
	@echo "    Installs package in your system."
	@echo "make uninstall"
	@echo "    uninstall package in your system."


install:
	@echo "Creazione Immagine request check"
	oc new-app openshift/python:3.9-ubi8~https://github.com/Gjonni/PseudoAdmissionController.git -n passbolt
	oc create  sa pseudoadmissioncontroller -n passbolt 
	oc label sa pseudoadmissioncontroller app=pseudoadmissioncontroller -n passbolt
	
	oc patch deployment pseudoadmissioncontroller -p '{"spec":{"template":{"spec":{"serviceAccount":"pseudoadmissioncontroller"}}}}' -n passbolt
	oc set env deployment/pseudoadmissioncontroller TZ=Europe/Rome NAMESPACES=passbolt EXCLUDE=pseudoadmissioncontroller LOGLEVEL=INFO -n passbolt 
	oc set env deployment/pseudoadmissioncontroller REQUEST_MEMORY='10Mi,20Mi' LIMITS_MEMORY='2Gi,4Gi' REQUEST_CPU='100m,200m' LIMITS_CPU='2,4' -n passbolt 
	oc scale deployment/pseudoadmissioncontroller --replicas=1 -n passbolt
	@echo "Fix Permission"
	oc adm policy add-role-to-user admin -z pseudoadmissioncontroller -n passbolt



uninstall:
	@echo "Disinstallo Applicazione"
	oc delete all --selector app=pseudoadmissioncontroller -n passbolt
	oc delete sa pseudoadmissioncontroller -n passbolt 

