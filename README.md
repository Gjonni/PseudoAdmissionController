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

|Variabile      |Esempio                  |Descrizione|
|---------------|-------------------------|-----------|
|TZ             |Europe/Rome              |           |
|NAMESPACES     |test\-namespace          |           |
|EXCLUDE        |PseudoAdmissionController|           |
|LOGLEVEL       |INFO                     |           |
|REQUEST\_MEMORY|10Mi,20Mi                |           |
|LIMITS\_MEMORY |2Gi,4Gi                  |           |
|REQUEST\_CPU   |100m,200m                |           |
|LIMITS\_CPU    |2,4                      |           |
