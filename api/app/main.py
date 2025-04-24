from fastapi import FastAPI, HTTPException
from typing import List
import uvicorn

from app.schemas import FilmInput, FilmPredictionResponse
from app.predict import predict_film_affluence

app = FastAPI(
    title="Film Affluence Prediction API",
    description="API pour prédire l'affluence des nouveaux films",
    version="1.0.1"
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
            prediction = predict_film_affluence(film)
            results.append({
                "title": film.title if hasattr(film, "title") else "Unknown",
                "predicted_affluence": prediction
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