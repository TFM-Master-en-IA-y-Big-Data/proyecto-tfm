from pydantic import BaseModel
from typing import List

class PredictionResponse(BaseModel):
    coin: str
    prediction: str
    probability: float
    current_price: float
    trend_data: List[float]
    risk_level: str