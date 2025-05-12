import pytest
from unittest.mock import patch, MagicMock
from app.predict import predict_film_affluence
from app.schemas import FilmInput

@pytest.fixture
def sample_input():
    return FilmInput(
        actors=["Cillian Murphy", "Clare Dunne", "Emily Watson"],
        date="2025-04-30T00:00:00",
        directors=["Tim Mielants"],
        editor="Condor Distribution",
        genre=["Drame"],
        langage=["Anglais"],
        length=98,
        nationality=["Irlande", "Belgique", "U.S.A."],
        title="Tu ne mentiras point"
    )

@patch("app.predict.load_model")
@patch("app.predict.transform_input")
@patch("app.predict.shap.TreeExplainer")
def test_predict_film_affluence(mock_shap_explainer, mock_transform_input, mock_load_model, sample_input):
    # --- Mock du modèle ---
    mock_model = MagicMock()
    mock_preprocessor = MagicMock()
    
    # simulate transform output
    mock_preprocessor.transform.return_value.toarray.return_value = [[1, 2, 3]]
    mock_preprocessor.get_feature_names_out.return_value = ['f1', 'f2', 'f3']
    
    mock_model.named_steps = {
        'preprocessor': mock_preprocessor,
        'xgboost': MagicMock(regressor_=MagicMock())
    }
    mock_model.predict.return_value = [999999]

    mock_load_model.return_value = mock_model

    # --- Mock transformation des données ---
    mock_transform_input.return_value = "processed_df"

    # --- Mock shap explainer ---
    mock_explainer_instance = MagicMock()
    mock_explainer_instance.return_value = "shap_values"
    mock_shap_explainer.return_value = mock_explainer_instance

    # --- Appel de la fonction ---
    prediction, shap_values_base64 = predict_film_affluence(sample_input, first=True)

    # --- Vérifications ---
    assert isinstance(prediction, float) or isinstance(prediction, int)
    assert prediction == 999999
    assert isinstance(shap_values_base64, str)
    assert len(shap_values_base64) > 0
