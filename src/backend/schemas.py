# src/backend/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class PredictionResponse(BaseModel):
    """Respuesta de predicción del API — modelo de regresión."""
    coin:            str
    prediction:      str           # "Subida" | "Bajada"
    probability:     float         # confidence normalizada [0, 1]
    current_price:   float         # precio actual en USD
    predicted_price: float         # precio predicho por el modelo
    variation_pct:   float         # variación % entre actual y predicho
    market_cap:      float
    trend_data:      List[float]   # últimos 7 precios normalizados [0-100]
    risk_level:      str           # "Bajo" | "Medio" | "Alto"
    confidence:      Optional[float] = None