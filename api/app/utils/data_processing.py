import pandas as pd
from app.schemas import FilmInput
from app.utils.azure_ml import get_national_affluence, get_max_average_actor

def transform_input(film_input: FilmInput):
    """
    Transforme les données d'entrée au format attendu par le modèle.
    
    Args:
        film_input: Données du film au format d'entrée de l'API
        
    Returns:
        DataFrame contenant les données formatées pour le modèle
    """
    print("on entre dans transform_input ")
    # Initialisation des variables
    french_prod = 1 if "France" in film_input.nationality else 0
    usa_prod = 1 if "U.S.A." in film_input.nationality or "U.S.A" in film_input.nationality else 0
    
    # Langues
    french_langage = 1 if any(lang.lower() in ["francais", "français", "french"] for lang in film_input.langage) else 0
    english_langage = 1 if any(lang.lower() in ["anglais", "english"] for lang in film_input.langage) else 0
    
    # Nombre d'acteurs
    number_actors = len(film_input.actors)
    
    # Récupération des données externes via Azure ML
    # Date formatée pour la fonction
    date_str = film_input.date.strftime("%Y-%m-%dT%H:%M:%S")
    print(pd.to_datetime(date_str))
    # Récupération de l'affluence nationale basée sur la date
    national_affluence = get_national_affluence(pd.to_datetime(date_str))
    print(f"national_affluence = {national_affluence}")
    
    # Récupération de la popularité maximale moyenne des acteurs
    max_average_actor = get_max_average_actor(film_input.actors)
    
    # Création du DataFrame au format attendu par le modèle
    data = [[
        french_prod, 
        pd.to_datetime(date_str),
        film_input.directors,
        film_input.editor,
        film_input.genre,
        film_input.length,
        number_actors,
        usa_prod,
        national_affluence,
        french_langage,
        english_langage,
        max_average_actor
    ]]
    
    columns = [
        "french_prod", 
        "date", 
        "directors", 
        "editor", 
        "genre", 
        "length", 
        "number_actors", 
        "usa_prod", 
        "national_affluence", 
        "french_langage", 
        "english_langage", 
        "max_average_actor"
    ]
    
    df = pd.DataFrame(data=data, columns=columns)
    
    return df