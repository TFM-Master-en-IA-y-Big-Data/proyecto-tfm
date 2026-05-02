# src/backend/main.py
"""
FastAPI Backend - Conecta el Pipeline ML con el Frontend
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config_pipeline import MODEL_PATH, DATASET_FEATURES_FILE, COINS
from src.logging_config import setup_logging
from src.backend.schemas import PredictionResponse
from src.backend.utils import cargar_modelo, obtener_prediccion_real

logger = setup_logging(__name__)

app = FastAPI(title="CryptoPredict API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ← Lista de monedas tomada directamente del config
ALLOWED_COINS = COINS  # ["bitcoin", "ethereum", "solana", "binancecoin", "ripple"]


@app.get("/")
def home():
    """Health check del API."""
    return {
        "mensaje": "CryptoPredict API",
        "status":  "online",
        "version": "2.0",
    }


@app.get("/model-status")
def model_status():
    """Verifica si el modelo está disponible."""
    try:
        model = cargar_modelo()
        if model is None:
            return {"status": "error", "mensaje": "Modelo no encontrado"}
        return {
            "status":         "ok",
            "modelo_cargado": True,
            "ruta":           str(MODEL_PATH),
        }
    except Exception as e:
        logger.error(f"[API] Error verificando modelo: {e}")
        return {"status": "error", "mensaje": str(e)}


@app.get("/predict/{symbol}", response_model=PredictionResponse)
async def get_prediction(symbol: str):
    """Predicción de precio para una crypto usando el modelo entrenado."""
    symbol_lower = symbol.lower()

    if symbol_lower not in ALLOWED_COINS:
        raise HTTPException(
            status_code=404,
            detail=f"Moneda no soportada. Disponibles: {ALLOWED_COINS}",
        )

    try:
        logger.info(f"[API] Predicción solicitada para {symbol_lower}")

        model = cargar_modelo()
        if model is None:
            raise HTTPException(
                status_code=500,
                detail="Modelo no disponible. Ejecuta primero: python src/pipeline_maestro.py",
            )

        result = obtener_prediccion_real(symbol_lower, model)
        logger.info(f"[API] Predicción completada para {symbol_lower}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Error en predicción: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/coins")
def get_available_coins():
    """Lista de monedas disponibles."""
    return {
        "coins": ALLOWED_COINS,
        "count": len(ALLOWED_COINS),
    }


@app.get("/metrics")
def get_metrics():
    """
    Métricas reales del modelo — se leen del CSV de evaluación si existe,
    si no devuelve un placeholder.
    """
    import pandas as pd
    from src.config_pipeline import OUTPUTS_DIR

    output_file = OUTPUTS_DIR / "predicciones_evaluacion.csv"

    try:
        if not output_file.exists():
            return {"status": "sin_evaluar", "mensaje": "Ejecuta evaluate.py primero"}

        df = pd.read_csv(output_file)
        mae  = float((df["y_real"] - df["y_predicho"]).abs().mean())
        rmse = float(((df["y_real"] - df["y_predicho"]) ** 2).mean() ** 0.5)

        return {
            "status":   "ok",
            "mae":      round(mae, 4),
            "rmse":     round(rmse, 4),
            "features": len([c for c in df.columns if c not in ["crypto", "timestamp"]]),
            "samples":  len(df),
        }
    except Exception as e:
        logger.error(f"[API] Error leyendo métricas: {e}")
        return {"status": "error", "mensaje": str(e)}


if __name__ == "__main__":
    import uvicorn
    logger.info("[API] Iniciando servidor FastAPI...")
    uvicorn.run(app, host="127.0.0.1", port=8000)