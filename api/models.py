from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Any

class MovieInput(BaseModel):
    actors: List[str]
    date: str
    directors: List[str]
    editor: str
    genre: List[str]
    langage: List[str]
    length: float
    nationality: List[str]

class MoviesRequest(BaseModel):
    movies: List[MovieInput]

class PredictionResult(BaseModel):
    film_index: int
    predicted_attendance: float

class PredictionsResponse(BaseModel):
    predictions: List[PredictionResult]