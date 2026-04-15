# src/backend/schemas.py
from pydantic import BaseModel
from typing import List

class PredictionResponse(BaseModel):
    """Respuesta de predicción del API"""
    coin: str
    prediction: str
    probability: float
    current_price: float
    market_cap: float
    trend_data: List[float]
    risk_level: str
    confidence: float = None