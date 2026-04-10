from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import PredictionResponse
from .utils import cargar_modelo
import random

app = FastAPI(title="CryptoPredict API")

# Permite que el frontend se conecte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"mensaje": "API de CryptoPredict Online"}

@app.get("/predict/{symbol}", response_model=PredictionResponse)
async def get_prediction(symbol: str):
    allowed = ["BTC", "ETH", "SOL", "BNB", "ADA"]
    if symbol.upper() not in allowed:
        raise HTTPException(status_code=404, detail="Moneda no encontrada")

    return {
        "coin": symbol.upper(),
        "prediction": random.choice(["Subida", "Bajada"]),
        "probability": round(random.uniform(0.6, 0.99), 2),
        "current_price": random.uniform(30000, 60000) if symbol.upper() == "BTC" else 2500,
        "trend_data": [random.uniform(10, 50) for _ in range(7)],
        "risk_level": random.choice(["Bajo", "Medio", "Alto"])
    }