import cloudpickle
import os
import pandas as pd
import numpy as np
from app.schemas import FilmInput
from app.utils.data_processing import transform_input
from app.utils.azure_ml import get_national_affluence, get_max_average_actor
import shap
import pickle
import base64

# Charger le modèle
MODEL_PATH = os.getenv("MODEL_PATH", "model/best_model.pkl")
MODEL2_PATH = os.getenv("MODEL2_PATH", "model/best_model_tuned.pkl")

def load_model(MODEL_PATH):
    """Charge le modèle depuis le fichier pkl"""
    try:
        with open(MODEL_PATH, "rb") as f:
            model = cloudpickle.load(f)
        return model
    except Exception as e:
        print(f"Erreur lors du chargement du modèle: {str(e)}")
        raise

def predict_film_affluence(film_input: FilmInput, first: bool) -> float:
    """
    Prédit l'affluence d'un film à partir des données d'entrée.
    Args:
        film_input: Données du film au format d'entrée de l'API
    Returns:
        Prédiction d'affluence
    """
    model = load_model(MODEL_PATH if first else MODEL2_PATH)
    preprocessor = model.named_steps['preprocessor']
    
    # Transformation des données d'entrée au format attendu par le modèle
    processed_data = transform_input(film_input)
    feature_names = preprocessor.get_feature_names_out()
    X_transformed = preprocessor.transform(processed_data)
    
    if hasattr(X_transformed, "toarray"):  # pour les sparse matrix
        X_transformed = X_transformed.toarray()
    
    X_transformed_df = pd.DataFrame(X_transformed, columns=feature_names)
    
    # Prédiction avec le modèle complet
    prediction = model.predict(processed_data)[0]
    
    # Extraction du modèle XGBoost final
    if first:
        # Vérifiez la structure réelle de votre pipeline
        if hasattr(model.named_steps['xgboost'], 'regressor_'):
            xgb_model = model.named_steps['xgboost'].regressor_
        else:
            xgb_model = model.named_steps['xgboost']
    else:
        xgb_model = model.named_steps['xgboost'].regressor_
    
    # Créer un explainer TreeExplainer spécifiquement pour XGBoost
    explainer = shap.TreeExplainer(xgb_model)
    
    # Pour les modèles XGBoost, utilisez directement X_transformed_df
    shap_values = explainer(X_transformed_df)

    # Sérialisation en string
    shap_values_bytes = pickle.dumps(shap_values)
    shap_values_base64 = base64.b64encode(shap_values_bytes).decode('utf-8')

    
    return prediction, shap_values_base64