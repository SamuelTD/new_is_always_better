from app.schemas import FilmInput
from app.predict import predict_film_affluence

def test_predict_film_affluence_integration():
    input_data = FilmInput(
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

    pred1, shap1 = predict_film_affluence(input_data, first=True)
    pred2, shap2 = predict_film_affluence(input_data, first=False)

    assert isinstance(pred1, float)
    assert isinstance(pred2, float)
    assert isinstance(shap1, str)
    assert isinstance(shap2, str)
    assert len(shap1) > 0
    assert len(shap2) > 0
