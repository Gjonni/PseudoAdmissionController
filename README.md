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
|LIMITS\_MEMORY |2Gi,4Gi                  |Impostare una                                                                 |
|REQUEST\_CPU   |100m,200m                |Impostare una                                                                 |
|LIMITS\_CPU    |2,4                      |Impostare una                                                                 |

**Disinstallazione**

1. Modificare le variabili all'interno del file makefile impostando le corrette configurazioni per il proprio cluster
2. Lanciare il comando di installazione

```
make uninstall
```

1. verificare che sul namespaces indicato ci sia il pod pseudoadmissioncontroller\-xxxxxxxx \( deployment \)
