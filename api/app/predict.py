import cloudpickle
import os
import pandas as pd
import numpy as np
from app.schemas import FilmInput
from app.utils.data_processing import transform_input
from app.utils.azure_ml import get_national_affluence, get_max_average_actor
import shap

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

def serialize_shap_payload(shap_values, base_value, feature_names, feature_values):
    """
    Sérialise les données SHAP en strings avec séparateurs pour stockage en base MSSQL.
    """
    shap_str = "|".join(f"{v:.12f}" for v in shap_values)
    features_str = "|".join(feature_names)
    values_str = "|".join(f"{v:.12f}" for v in feature_values)
    base_str = f"{base_value:.12f}"

    return f"{shap_str};{base_str};{features_str};{values_str}"

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
    shap_values = explainer.shap_values(X_transformed_df)
    
    # Si shap_values est un array simple (pas un objet Explanation)
    if isinstance(shap_values, np.ndarray):
        shap_values_list = shap_values[0].tolist()
        base_value = explainer.expected_value
    else:  # Si c'est un objet Explanation
        shap_values_list = shap_values.values[0].tolist()
        base_value = shap_values.base_values[0]
    
    feature_values = X_transformed_df.iloc[0].tolist()
    
    return prediction, serialize_shap_payload(shap_values_list, base_value, feature_names.tolist(), feature_values)


# def predict_film_affluence(film_input: FilmInput,first: bool) -> float:
#     """
#     Prédit l'affluence d'un film à partir des données d'entrée.
    
#     Args:
#         film_input: Données du film au format d'entrée de l'API
        
#     Returns:
#         Prédiction d'affluence
#     """
#     model = load_model(MODEL_PATH if first else MODEL2_PATH)
#     preprocessor = model.named_steps['preprocessor']
#     if first :
#         xgb_model = model.named_steps['xgboost'] #.regressor_
#     else:
#         xgb_model = model.named_steps['xgboost'].regressor_
#     # Transformation des données d'entrée au format attendu par le modèle

#     processed_data = transform_input(film_input)
#     feature_names = preprocessor.get_feature_names_out()

#     X_transformed = preprocessor.transform(processed_data)
#     if hasattr(X_transformed, "toarray"):  # pour les sparse matrix
#         X_transformed = X_transformed.toarray()
#     X_transformed_df = pd.DataFrame(X_transformed, columns=feature_names)
#     explainer = shap.Explainer(xgb_model, X_transformed_df)
#     shap_values = explainer(X_transformed_df)
#     shap_values_list = shap_values.values[0].tolist()
#     base_value = shap_values.base_values[0]
#     feature_values = X_transformed_df.iloc[0].tolist()

#     # Prédiction avec le modèle
#     prediction = model.predict(processed_data)[0]
#     return prediction, serialize_shap_payload(shap_values_list, base_value, feature_names.tolist(), feature_values)