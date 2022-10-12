# PseudoAdmissionController

La necessità è di avere un controllo sulle risorse dei singoli container, nello specifico Requests e Limits, per le versioni più vecchie, dove gli AdmissionController non sono presenti.

L'admission Controller normalmente intercettano le chiamate effettuate verso le API di Kubernetes/Openshift e verificano se i requisiti impostati vengono rispettati.

PseudoAdmissionController effettua un controllo molto simile ma a posteriori dal rilascio infatti verifica le REquests e i Limits di  ogni risorsa che genera un pod applicativo, quali Deployment, DeploymentConfig, Statefulset etc.

**Installazione**

1. Modificare le variabili all'interno del file makefile impostando le corrette configurazioni per il proprio cluster
2. Lanciare il comando di installazione

```
make install
```

1. verificare che sul namespaces indicato ci sia il pod pseudoadmissioncontroller\-xxxxxxxx \( deployment \)

**Configurazione**

**Variabili d'ambiente**

|Variabile      |Esempio                  |Descrizione                                                                   |
|---------------|-------------------------|------------------------------------------------------------------------------|
|TZ             |Europe/Rome              |Impostare il timezone del micro\-servizio                                     |
|NAMESPACES     |test\-namespace          |Impostare una lista i namespaces da tenere sotto controllo                    |
|EXCLUDE        |PseudoAdmissionController|Escludere il nome di un oggetto es. nome della Deployment,DeploymentConfig etc|
|LOGLEVEL       |INFO                     |Impostare il livello di verbosità                                             |
|REQUEST\_MEMORY|10Mi,20Mi                |Impostare una Whitelist di valori ( separati dal virgola) tutti quelli non presenti nella lista andranno a comporre una BlackList                                                                 |
|LIMITS\_MEMORY |2Gi,4Gi                  |Impostare una Whitelist di valori ( separati dal virgola) tutti quelli non presenti nella lista andranno a comporre una BlackList                                                                 |
|REQUEST\_CPU   |100m,200m                |Impostare una Whitelist di valori ( separati dal virgola) tutti quelli non presenti nella lista andranno a comporre una BlackList                                                                 |
|LIMITS\_CPU    |2,4                      |Impostare una Whitelist di valori ( separati dal virgola) tutti quelli non presenti nella lista andranno a comporre una BlackList                                                                 |



**Utilizzo**

1. Come primo step vi è la connessione al cluster utilizzando il token del serviceAccount PseudoAdmissionController

```
if "OPENSHIFT_BUILD_NAME" in os.environ:
    kubernetes.config.load_incluster_config()
    file_namespace = open("/run/secrets/kubernetes.io/serviceaccount/namespace", "r")
    if file_namespace.mode == "r":
        namespace = file_namespace.read()
        print(f"namespace: { namespace }")
else:
    kubernetes.config.load_kube_config()
    namespace = "passbolt". ## Modificare il namespace nel caso il file python venisse lanciato manualmente
```

1. Il microservizio verifica che tutte le variabili d'ambiente necessarie al corretto funzionamento siano configurate

```
import os
from library.Logging import Logging
class ValidationEnviroment:
    def __init__(self):
        self.namespaces = os.environ.get("NAMESPACES")
        self.excludeObject = os.environ.get("EXCLUDE")
        self.requestMemory = os.environ.get("REQUEST_MEMORY")
        self.requestCpu = os.environ.get("REQUEST_CPU")
        self.limitsMemory = os.environ.get("LIMITS_MEMORY")
        self.limitsCpu = os.environ.get("LIMITS_CPU")
    @property
    def namespaces(self):
        return self._namespaces
    @namespaces.setter
    def namespaces(self, value):
        Logging.logger.debug(f"I Namespaces verificati sono {value}")
        if not value:
            raise ValueError("NAMESPACES is not set.")
        self._namespaces = value.split(',')
    @property
    def excludeObject(self):
        return self._excludeObject
    @excludeObject.setter
    def excludeObject(self, value):
        Logging.logger.debug(f"Gli oggetti esclusi dalla verifica sono {value}")
        if not value:
            raise ValueError("List Object BlackList is not set.")
        self._excludeObject = value.split(',')
    @property
    def requestMemory(self):
        return self._requestMemory
    @requestMemory.setter
    def requestMemory(self, value):
        Logging.logger.debug(f"La whitelist della Request Memory {value}")
        if not value:
            raise ValueError("Request Memory  is not set.")
        self._requestMemory = value.split(',')
    @property
    def requestCpu(self):
        return self._requestCpu
    @requestCpu.setter
    def requestCpu(self, value):
        Logging.logger.debug(f"La whitelist della Request CPU {value}")
        if not value:
            raise ValueError("Request Cpu  is not set.")
        self._requestCpu = value.split(',')
    @property
    def limitsMemory(self):
        return self._limitsMemory
    @limitsMemory.setter
    def limitsMemory(self, value):
        Logging.logger.debug(f"La whitelist della Limits Memory {value}")
        if not value:
            raise ValueError("Limits Memory  is not set.")
        self._limitsMemory = value.split(',')
    @property
    def limitsCpu(self):
        return self._limitsCpu
    @limitsCpu.setter
    def limitsCpu(self, value):
        Logging.logger.debug(f"La whitelist della Limits CPU {value}")
        if not value:
            raise ValueError("Limits Cpu  is not set.")
        self._limitsCpu = value.split(',')
```

1. Verifica se l'oggetto che non rispetta i requisiti faccia parte della lista dei namespace inseriti nella relativa variabile d'ambiente 

```
        if not (
            object["object"].metadata.namespace in ValidationEnviroment().namespaces
            and object["object"].metadata.name not in ValidationEnviroment().excludeObject
        ):
            continue
        if object["type"] not in ["ADDED", "MODIFIED"]:
            continue
```

1. Infine Scala a 0 tutti i micro\-servizi che non rispettano i valori presenti nelle Whitelist  di Request e Limits configurate nelle relative variabili d'ambiente

```
            if (container.resources.requests.memory not in ValidationEnviroment().requestMemory):
                Logging.logger.info(f"{ThreadName } - Policy Violation from Container { container.name } - nella { kind } { object['object'].metadata.name } - requests ram: { container.resources.requests.memory} in namespace { object['object'].metadata.namespace } - Scale to 0 ")
                scale_down( object["object"].kind, object["object"].metadata.name, object["object"].metadata.namespace,)
            if (container.resources.requests.cpu not in ValidationEnviroment().requestCpu):
                Logging.logger.info(f"{ThreadName } - Policy Violation from Container { container.name } - nella { kind } { object['object'].metadata.name } - requests cpu: { container.resources.requests.cpu} in namespace { object['object'].metadata.namespace } - Scale to 0 ")
                scale_down( object["object"].kind, object["object"].metadata.name, object["object"].metadata.namespace,)
```





**Disinstallazione**

1. Modificare le variabili all'interno del file makefile impostando le corrette configurazioni per il proprio cluster
2. Lanciare il comando di installazione

```
make uninstall
```

1. verificare che sul namespaces indicato ci sia il pod pseudoadmissioncontroller\-xxxxxxxx \( deployment \)
