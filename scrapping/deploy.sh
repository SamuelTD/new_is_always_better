### 0) CONFIGURATION –– adapte ces valeurs
RG="gvanessonRG"
LOCATION="francecentral"
STORAGE_ACCOUNT="airflowsa"
Afficher plus
message.txt
5 Ko
﻿
``` py

### 0) CONFIGURATION –– adapte ces valeurs
RG="gvanessonRG"
LOCATION="francecentral"
STORAGE_ACCOUNT="airflowsa"
FILE_SHARE="airflow-share"
ACI_NAME="airflow-aci"
DNS_LABEL="airflowaci"       # doit être unique
URL_FILE_SHARE="http://${STORAGE_ACCOUNT}.file.core.windows.net/${FILE_SHARE}"

### 1) Vérif RG
if ! az group exists --name "$RG" | grep -q true; then
  echo "❌ RG '$RG' introuvable. Crée-le d’abord."
  exit 1
fi

### 2) Création ou réutilisation du Storage Account
if ! az storage account show -n "$STORAGE_ACCOUNT" -g "$RG" &>/dev/null; then
  echo "→ Création du Storage Account '$STORAGE_ACCOUNT'..."
  az storage account create \
    -n "$STORAGE_ACCOUNT" \
    -g "$RG" \
    -l "$LOCATION" \
    --sku Standard_LRS
else
  echo "→ Storage Account '$STORAGE_ACCOUNT' existe déjà."
fi

### 3) Récup clé & export
KEY=$(az storage account keys list -g "$RG" -n "$STORAGE_ACCOUNT" --query "[0].value" -o tsv)
export AZURE_STORAGE_ACCOUNT="$STORAGE_ACCOUNT"
export AZURE_STORAGE_KEY="$KEY"

echo "→ La clé est  '$KEY'..."

az storage file delete \
  --share-name airflow-share \
  --path airflow.db

### 4) File Share
if ! az storage share exists --name "$FILE_SHARE" -o tsv | grep -q true; then
  echo "→ Création du File Share '$FILE_SHARE'..."
  az storage share create --name "$FILE_SHARE"
else
  echo "→ File Share '$FILE_SHARE' existe déjà."
fi

### 5) Upload des DAGs, logs, etc.
echo "→ Upload dans '$FILE_SHARE'…"
az storage file upload-batch --destination "$URL_FILE_SHARE" --source "./dags"          --destination-path "dags"
az storage file upload-batch --destination "$URL_FILE_SHARE" --source "./logs"          --destination-path "logs"
az storage file upload-batch --destination "$URL_FILE_SHARE" --source "./plugins"       --destination-path "plugins"
az storage file upload-batch --destination "$URL_FILE_SHARE" --source "./Movie_Predict" --destination-path "Movie_Predict"
az storage file upload       -s "$FILE_SHARE" --source "./requirements.txt"

### 6) Génération du YAML ACI
cat > container-group.yaml <<EOF
apiVersion: '2018-10-01'
location: francecentral
name: airflow-aci
properties:
  osType: Linux
  restartPolicy: Never
  ipAddress:
    type: Public
    dnsNameLabel: airflowaci
    ports:
      - port: 8080
  containers:
    - name: airflow
      properties:
        image: apache/airflow:2.10.5-python3.10
        resources:
          requests:
            cpu: 1
            memoryInGb: 4
        environmentVariables:
          - name: AIRFLOW__CORE__EXECUTOR
            value: SequentialExecutor
          - name: AIRFLOW__CORE__FERNET_KEY
            value: 'hHtPQNnmanLorXPPGZ5ZhriWQOYCHYxykpQvmeTnaiY='
          - name: AIRFLOW__CORE__LOAD_EXAMPLES
            value: 'false'
          - name: AIRFLOW__WEBSERVER__WEB_SERVER_PORT
            value: '8080'
          - name: AIRFLOW__LOGGING__USE_SYMLINK
            value: "False"
        volumeMounts:
          - name: airflow-share
            mountPath: /opt/airflow
        ports:
          - port: 8080
        command:
          - bash
          - -c
          - |
            set -e
            # 1) Installer les libs
            pip install -r /opt/airflow/requirements.txt

            #1 bis 
            airflow db upgrade

            # 2) Lancer Airflow en "standalone" (SQLite + webserver + scheduler)
            exec airflow standalone 
  volumes:
    - name: airflow-share
      azureFile:
        shareName: airflow-share
        storageAccountName: airflowsa
        storageAccountKey: ${KEY}
EOF

### 7) Recréation du groupe
if az container show -g "$RG" -n "$ACI_NAME" &>/dev/null; then
  echo "→ Suppression de l’ancien ACI '$ACI_NAME'…"
  az container delete -g "$RG" -n "$ACI_NAME" --yes
fi

echo "→ Déploiement du Container Group '$ACI_NAME'…"
az container create -g "$RG" -f container-group.yaml

echo "✅ Terminé !
• UI ➜ http://$DNS_LABEL.$LOCATION.azurecontainer.io:8080
• RG    : $RG
• Share : $STORAGE_ACCOUNT/$FILE_SHARE"
```
message.txt
5 Ko