from fastapi import FastAPI, HTTPException
from typing import List
import uvicorn

from app.schemas import FilmInput, FilmPredictionResponse
from app.predict import predict_film_affluence

app = FastAPI(
    title="Film Affluence Prediction API",
    description="API pour prédire l'affluence des nouveaux films",
    version="1.0.2"
)

@app.post("/predict", response_model=FilmPredictionResponse)
async def predict_affluence(films: List[FilmInput]):
    """
    Prédit l'affluence pour une liste de films.
    
    Chaque film est spécifié avec ses métadonnées comme les acteurs, réalisateurs, etc.
    """
    try:
        results = []
        for film in films:
            prediction, shap = predict_film_affluence(film, True)
            prediction2, shap2 = predict_film_affluence(film, False)
            if shap == None:
                shap = ""
            if shap2 == None:
                shap2 = ""
            results.append({
                "title": film.title if hasattr(film, "title") else "Unknown",
                "predicted_affluence": prediction,
                "shap_values": shap,
                "second_predicted_affluence": prediction2,
                "second_shap_values": shap2
            })
        return {"predictions": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Endpoint de vérification de l'état de l'API"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)