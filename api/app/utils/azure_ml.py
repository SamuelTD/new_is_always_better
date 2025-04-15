import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
import os

# # Configuration Azure
# SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "72eb7803-e874-44cb-b6d9-33f2fa3eb88c")
# RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", "vpoutotrg")
# WORKSPACE_NAME = os.getenv("AZURE_WORKSPACE_NAME", "mlstudio-groupe4")

# TENANT_ID = os.getenv("AZURE_TENANT_ID")
# CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
# CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

# # Initialisation du client Azure ML
# def get_ml_client():
#     """Initialise et retourne un client Azure ML."""
#     try:
#         credential = DefaultAzureCredential()
#         ml_client = MLClient(
#             credential=credential,
#             subscription_id=SUBSCRIPTION_ID,
#             resource_group_name=RESOURCE_GROUP,
#             workspace_name=WORKSPACE_NAME
#         )
#         return ml_client
#     except Exception as e:
#         print(f"Erreur lors de l'initialisation du client Azure ML: {str(e)}")
#         raise

# Cache pour stocker les données récupérées
_actors_data = None
_national_affluence_data = None

def load_actors_data():
    """Charge les données des acteurs depuis Azure ML"""
    global _actors_data
    
    if _actors_data is not None:
        return _actors_data
    
    # ml_client = get_ml_client()
    # file_name = "actors_jpbox"
    # version = "2.0"
    
    # data_asset = ml_client.data.get(file_name, version=version)
    df_actors = pd.read_parquet("app/utils/actors_docker.parquet")
    print(df_actors)
    # Prétraitement des noms d'acteurs
    df_actors['name'] = df_actors["name"].apply(
        lambda x: x.replace(" ", "").replace("-", "").replace("_", "").strip().lower()
    )
    df_actors.set_index('name', inplace=True)
    
    _actors_data = df_actors
    return _actors_data

def load_national_affluence_data():
    """Charge les données d'affluence nationale depuis Azure ML"""
    global _national_affluence_data
    
    if _national_affluence_data is not None:
        return _national_affluence_data
    
    # ml_client = get_ml_client()
    # file_name = "cncAffluence"
    # version = "2.0.1"
    
    # data_asset = ml_client.data.get(file_name, version=version)
    _national_affluence_data = pd.read_parquet("app/utils/affluence_docker.parquet")
    
    return _national_affluence_data

def get_max_average_actor(actors):
    """
    Récupère la valeur max_average_actor basée sur la liste des acteurs.
    
    Args:
        actors: Liste des noms d'acteurs
        
    Returns:
        Valeur max_average_actor
    """
    df_actors = load_actors_data()
    
    # Prétraitement des noms d'acteurs de la requête
    processed_actors = [
        actor.replace(" ", "").replace("-", "").replace("_", "").strip().lower()
        for actor in actors
    ]
    
    # Récupération des scores pour les acteurs présents dans la base
    actor_scores = []
    for actor in processed_actors:
        if actor in df_actors.index:
            # Supposons que la colonne "boxoffice_average" contient la valeur recherchée
            actor_scores.append(df_actors.loc[actor, "boxoffice_average"])
    
    # Si aucun acteur n'est trouvé, retourner une valeur par défaut
    if not actor_scores:
        return 0
    
    # Retourner le score maximum
    return max(actor_scores)

def get_national_affluence(date):
    """
    Récupère la valeur national_affluence basée sur la date.
    
    Args:
        date: Datetime
        
    Returns:
        Valeur national_affluence
    """
    # Charger les données d'affluence
    df_affluence = load_national_affluence_data()
    
    # Convertir la date en objet datetime correspondant à la data
    date = pd.to_datetime(f"{date.year}-{date.month:02d}-01")
    
    # Retourner la valeur d'affluence pour la date du mois correspondant
    return df_affluence.loc[date, 'box_office'] if date in df_affluence.index else None