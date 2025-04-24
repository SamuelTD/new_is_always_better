from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class FilmInput(BaseModel):
    """Modèle d'entrée pour les prédictions de films"""
    actors: List[str] = Field(..., description="Liste des acteurs du film")
    date: datetime = Field(..., description="Date de sortie du film")
    directors: List[str] = Field(..., description="Liste des réalisateurs du film")
    editor: str = Field(..., description="Éditeur/distributeur du film")
    genre: List[str] = Field(..., description="Genres du film")
    langage: List[str] = Field(..., description="Langues du film")
    length: float = Field(..., description="Durée du film en minutes")
    nationality: List[str] = Field(..., description="Nationalités de production du film")
    title: Optional[str] = Field(None, description="Titre du film (optionnel)")

class FilmPrediction(BaseModel):
    """Résultat de prédiction pour un film"""
    title: str
    predicted_affluence: float

class FilmPredictionResponse(BaseModel):
    """Réponse contenant les prédictions pour tous les films"""
    predictions: List[FilmPrediction]