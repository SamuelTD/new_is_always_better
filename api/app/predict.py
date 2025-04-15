import cloudpickle
import os
import pandas as pd
from app.schemas import FilmInput
from app.utils.data_processing import transform_input
from app.utils.azure_ml import get_national_affluence, get_max_average_actor


# Charger le modèle
MODEL_PATH = os.getenv("MODEL_PATH", "model/best_model.pkl")

def load_model():
    """Charge le modèle depuis le fichier pkl"""
    try:
        with open(MODEL_PATH, "rb") as f:
            model = cloudpickle.load(f)
        return model
    except Exception as e:
        print(f"Erreur lors du chargement du modèle: {str(e)}")
        raise

# Charger le modèle au démarrage
model = load_model()

def predict_film_affluence(film_input: FilmInput) -> float:
    """
    Prédit l'affluence d'un film à partir des données d'entrée.
    
    Args:
        film_input: Données du film au format d'entrée de l'API
        
    Returns:
        Prédiction d'affluence
    """
    print("on entre dans predict_film_affluence ")
    # Transformation des données d'entrée au format attendu par le modèle
    processed_data = transform_input(film_input)
    
    # Prédiction avec le modèle
    prediction = model.predict(processed_data)[0]
    
    return prediction