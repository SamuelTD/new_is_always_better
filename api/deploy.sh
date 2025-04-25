#!/bin/bash

# Charger les variables d'environnement depuis le fichier .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "⚠️ Fichier .env introuvable !"
    exit 1
fi

# Variables
RESOURCE_GROUP="vpoutotRG"
CONTAINER_NAME="api-luvirasa"
ACR_NAME="vpoutotRegistry"
ACR_LOGIN_SERVER="vpoutotregistry.azurecr.io"
IMAGE_NAME="$ACR_LOGIN_SERVER/apinewsisalwaysbetter:latest"
PORT=80
RESTART_POLICY="OnFailure"
OS_TYPE="Linux"  

# Récupérer les identifiants ACR
ACR_CREDENTIALS=$(az acr credential show --name $ACR_NAME --query "{username:username,password:passwords[0].value}" --output json)
ACR_USERNAME=$(echo $ACR_CREDENTIALS | jq -r .username)
ACR_PASSWORD=$(echo $ACR_CREDENTIALS | jq -r .password)

# Variables d'environnement pour le conteneur
ENV_VARS=(
    "MODEL_PATH=$MODEL_PATH" 
    "MODEL2_PATH=$MODEL2_PATH"
)

# Connexion à Azure (si nécessaire)
echo "🔐 Connexion à Azure..."
az account show > /dev/null 2>&1
if [ $? -ne 0 ]; then
    az login
fi

# Connexion à Azure Container Registry (ACR)
echo "🔐 Connexion à ACR..."
az acr login --name $ACR_NAME

# Vérification si l'instance ACI existe déjà
echo "🔍 Vérification de l'existence de l'instance..."
az container show --name $CONTAINER_NAME --resource-group $RESOURCE_GROUP > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "♻️ L'instance existe déjà, suppression en cours..."
    az container delete --name $CONTAINER_NAME --resource-group $RESOURCE_GROUP --yes
    echo "⌛ Attente 10 secondes pour suppression..."
    sleep 10
fi

# Création de l'instance ACI
echo "🚀 Déploiement du conteneur..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image $IMAGE_NAME \
    --dns-name-label api-luvirasa \
    --cpu 1 --memory 1.5 \
    --ip-address Public \
    --ports $PORT \
    --restart-policy $RESTART_POLICY \
    --registry-login-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --os-type $OS_TYPE \
    --environment-variables MODEL_PATH="$MODEL_PATH" MODEL2_PATH="$MODEL2_PATH" 
    
# Vérification du statut du conteneur
echo "⏳ Vérification du statut du conteneur..."
az container show --name $CONTAINER_NAME --resource-group $RESOURCE_GROUP --query "{Status:instanceView.state,IP:ipAddress.ip}" --output table

echo "✅ Déploiement terminé ! 🎉"