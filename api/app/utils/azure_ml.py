import pandas as pd
import os
import json

# Cache pour stocker les données récupérées
_actors_data = None
_national_affluence_data = None

def load_actors_data():
    """Charge les données des acteurs depuis le fichier parquet"""
    global _actors_data
    
    if _actors_data is not None:
        return _actors_data

    df_actors = pd.read_parquet("app/utils/actors_docker.parquet")
    # Prétraitement des noms d'acteurs
    df_actors['name'] = df_actors["name"].apply(
        lambda x: x.replace(" ", "").replace("-", "").replace("_", "").strip().lower()
    )
    df_actors.set_index('name', inplace=True)
    
    _actors_data = df_actors
    return _actors_data

def load_national_affluence_data():
    """Charge les données d'affluence nationale depuis le fichier parquet"""
    global _national_affluence_data
    
    if _national_affluence_data is not None:
        return _national_affluence_data

    _national_affluence_data = pd.read_parquet("app/utils/affluence_docker.parquet")
    
    return _national_affluence_data

def get_max_average_actor(actors):
    df_actors = load_actors_data()

    # Prétraitement des noms d'acteurs de la requête
    processed_actors = [
        actor.replace(" ", "").replace("-", "").replace("_", "").strip().lower()
        for actor in actors
    ]

    scores = []
    for actor in processed_actors:
        if actor in df_actors.index :
            scores.append(df_actors.loc[actor, "boxoffice_average"])
    scores.sort(reverse=True)
    return scores

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

def get_target_encoding(genre, langage, nationality, directors, actors):
    """
    Récupère et calcule les valeurs d'encodage cible pour différentes caractéristiques d'un film.
    
    Cette fonction charge un dictionnaire d'encodage cible à partir d'un fichier JSON,
    puis extrait les scores associés à chaque élément des listes fournies.
    Pour chaque catégorie, les trois meilleurs scores sont retenus.
    
    Paramètres:
        genre (list): Liste des genres du film
        langage (list): Liste des langues du film
        nationality (list): Liste des nationalités associées au film
        directors (list): Liste des réalisateurs du film
        actors (list): Liste des acteurs du film
        
    Retourne:
        dict: Dictionnaire contenant les trois meilleurs scores d'encodage pour chaque catégorie
    """
    # Chargement du dictionnaire d'encodage cible depuis le fichier JSON
    with open('app/utils/target_encoding_list.json', 'r', encoding='utf-8') as f:
        target_encoding_dict = json.load(f)
    
    # Liste des noms de colonnes correspondant aux paramètres d'entrée
    str_list = ["genre", "langage", "nationality", 'directors', "actors"]
    
    # Dictionnaire pour stocker les résultats
    result = {}
    
    # Parcours de chaque liste de caractéristiques
    for i, col_list in enumerate([genre, langage, nationality, directors, actors]):
        col_key = str_list[i]
        scores = []
        
        # Récupération des scores d'encodage pour chaque élément de la liste
        for item in col_list:
            if item in target_encoding_dict.get(col_key, {}):
                scores.append(target_encoding_dict[col_key][item])
        
        # Tri des scores par ordre décroissant
        scores = sorted(scores, reverse=True)
        
        # Stockage des trois meilleurs scores dans le dictionnaire de résultats
        # Si moins de trois scores sont disponibles, utilisation de 0 comme valeur par défaut
        result[f'{col_key}_first_target_transform'] = scores[0] if len(scores) > 0 else 0
        result[f'{col_key}_second_target_transform'] = scores[1] if len(scores) > 1 else 0
        result[f'{col_key}_third_target_transform'] = scores[2] if len(scores) > 2 else 0
    
    return result

