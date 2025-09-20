from pydantic import BaseModel, validator
from typing import Optional


class GenrePredictionRequest(BaseModel):
    total_spent: Optional[float] = 0.0
    total_tracks_bought: Optional[int] = 0
    genre_spending_ratio: Optional[float] = 0.0
    
    @validator("total_spent")
    def validate_total_spent(cls, total_spent):
        if total_spent is None or total_spent < 0:
            return 0.0
        return float(total_spent)
    
    @validator("total_tracks_bought")
    def validate_total_tracks_bought(cls, total_tracks_bought):
        if total_tracks_bought is None or total_tracks_bought < 0:
            return 0
        return int(total_tracks_bought)
    
    @validator("genre_spending_ratio")
    def validate_genre_spending_ratio(cls, genre_spending_ratio):
        if genre_spending_ratio is None or genre_spending_ratio < 0:
            return 0.0
        return min(float(genre_spending_ratio), 1.0)  # Cap at 1.0


class GenrePrediction(BaseModel):
    genre: str
    confidence: float
    all_probabilities: dict


class GenrePredictionResponse(BaseModel):
    status: str
    prediction: GenrePrediction
    customer_profile: dict