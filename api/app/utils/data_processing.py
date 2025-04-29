import pandas as pd
from app.schemas import FilmInput
from app.utils.azure_ml import get_national_affluence, get_max_average_actor, get_target_encoding

def num_list_col(x):
    """
    Pour mettre 0 au nombre lorsque la valeur est 'no value'
    """
    n = len(x)
    if n==1:
        if x[0]=="no value":
            n=0
    return n

def transform_input(film_input: FilmInput):
    """
    Transforme les données d'entrée au format attendu par le modèle.
    
    Args:
        film_input: Données du film au format d'entrée de l'API
        
    Returns:
        DataFrame contenant les données formatées pour le modèle
    """
    # Initialisation des variables
    french_prod = 1 if "France" in film_input.nationality else 0
    usa_prod = 1 if "U.S.A." in film_input.nationality or "U.S.A" in film_input.nationality else 0
    japan_prod = 1 if "Japon" in film_input.nationality else 0
    uk_prod = 1 if "Grande-Bretagne" in film_input.nationality or 'UK' in film_input.nationality or 'United Kingdom' in film_input.nationality else 0
    italy_prod = 1 if 'Italie' in film_input.nationality or 'Italy' in film_input.nationality else 0
    spain_prod = 1 if 'Espagne' in film_input.nationality or 'Spain' in film_input.nationality else 0
    germany_prod = 1 if 'Allemagne' in film_input.nationality or 'Germany' in film_input.nationality else 0
    nationality_count = num_list_col(film_input.nationality)
    
    # Langues
    french_langage = 1 if any(lang.lower() in ["francais", "français", "french"] for lang in film_input.langage) else 0
    english_langage = 1 if any(lang.lower() in ["anglais", "english"] for lang in film_input.langage) else 0
    language_count = num_list_col(film_input.langage)
    
    # Nombre d'acteurs
    number_actors = num_list_col(film_input.actors)
    
    # Récupération des données externes via Azure ML
    # Date formatée pour la fonction
    date_str = film_input.date #.strftime("%Y-%m-%dT%H:%M:%S")
    # Récupération de l'affluence nationale basée sur la date
    national_affluence = get_national_affluence(pd.to_datetime(date_str))
    
    # Récupération de la popularité maximale moyenne des acteurs à partir de jpbox
    list_average_actor = get_max_average_actor(film_input.actors)
    max_average_actor = list_average_actor[0] if len(list_average_actor)>0 else 0
    second_max_average_actor = list_average_actor[1] if len(list_average_actor)>1 else 0
    third_max_average_actor = list_average_actor[2] if len(list_average_actor)>2 else 0

    # Target encoding des listes
    dict_target_encoding = get_target_encoding(film_input.genre, film_input.langage, film_input.nationality, film_input.directors, film_input.actors)
    for col in ["genre", "langage", "nationality", "directors", "actors"]:
        dict_target_encoding
    
    # Création du DataFrame au format attendu par le modèle
    data = [[
        french_prod, 
        pd.to_datetime(date_str),
        film_input.editor,
        film_input.length,
        number_actors,
        usa_prod,
        japan_prod,
        national_affluence,
        french_langage,
        english_langage,
        max_average_actor,
        second_max_average_actor,
        third_max_average_actor,
        nationality_count,
        germany_prod,
        spain_prod,
        italy_prod,
        uk_prod,
        language_count,
        dict_target_encoding["genre_first_target_transform"], 
        dict_target_encoding["genre_second_target_transform"],
        dict_target_encoding["genre_third_target_transform"],
        dict_target_encoding["langage_first_target_transform"], 
        dict_target_encoding["langage_second_target_transform"],
        dict_target_encoding["langage_third_target_transform"], 
        dict_target_encoding["nationality_first_target_transform"],
        dict_target_encoding["nationality_second_target_transform"],
        dict_target_encoding["nationality_third_target_transform"],
        dict_target_encoding["directors_first_target_transform"],
        dict_target_encoding["directors_second_target_transform"],
        dict_target_encoding["directors_third_target_transform"],
        dict_target_encoding["actors_first_target_transform"], 
        dict_target_encoding["actors_second_target_transform"],
        dict_target_encoding["actors_third_target_transform"]
    ]]

    columns = [
        'french_prod',
        'date',
        'editor',
        'length',
        'number_actors',
        'usa_prod',
        'japan_prod',
        'national_affluence',
        'french_langage', 
        'english_langage',
        'max_average_actor',
        'second_max_average_actor',
        'third_max_average_actor',  
        'nationality_count', 
        'germany_prod', 
        'spain_prod', 
        'italy_prod', 
        'uk_prod', 
        'language_count', 
        'genre_first_target_transform', 
        'genre_second_target_transform',
        'genre_third_target_transform',
        'langage_first_target_transform', 
        'langage_second_target_transform',
        'langage_third_target_transform', 
        'nationality_first_target_transform',
        'nationality_second_target_transform',
        'nationality_third_target_transform',
        'directors_first_target_transform',
        'directors_second_target_transform',
        'directors_third_target_transform',
        'actors_first_target_transform', 
        'actors_second_target_transform',
        'actors_third_target_transform'
    ]
    
    df = pd.DataFrame(data=data, columns=columns)
    
    return df