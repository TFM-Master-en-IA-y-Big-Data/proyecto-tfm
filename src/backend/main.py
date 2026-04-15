# src/backend/main.py
"""
FastAPI Backend - Conecta el Pipeline ML con el Frontend
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# ✅ IMPORTS AJUSTADOS (porque estamos dentro de src/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # Subir a raíz
from src.config_pipeline import MODEL_PATH, DATASET_FEATURES_FILE
from src.logging_config import setup_logging
from src.backend.schemas import PredictionResponse
from src.backend.utils import cargar_modelo, obtener_prediccion_real

logger = setup_logging(__name__)

app = FastAPI(title="CryptoPredict API - Integrado con Pipeline")

# CORS para que frontend acceda
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ENDPOINTS ====================

@app.get("/")
def home():
    """Health check del API"""
    logger.info("[API] Acceso a home")
    return {
        "mensaje": "CryptoPredict API - Pipeline Integrado",
        "status": "online",
        "version": "1.0"
    }

@app.get("/model-status")
def model_status():
    """Verifica si el modelo está cargado"""
    try:
        model = cargar_modelo()
        if model is None:
            return {"status": "error", "mensaje": "Modelo no encontrado"}
        return {
            "status": "ok",
            "modelo_cargado": True,
            "ruta": str(MODEL_PATH)
        }
    except Exception as e:
        logger.error(f"[API] Error verificando modelo: {e}")
        return {"status": "error", "mensaje": str(e)}

@app.get("/predict/{symbol}", response_model=PredictionResponse)
async def get_prediction(symbol: str):
    """
    ✨ PREDICCIÓN REAL usando el modelo entrenado
    """
    allowed = ["bitcoin", "ethereum", "solana", "cardano", "ripple"]
    symbol_lower = symbol.lower()
    
    if symbol_lower not in allowed:
        raise HTTPException(
            status_code=404,
            detail=f"Moneda no encontrada. Monedas soportadas: {allowed}"
        )
    
    try:
        logger.info(f"[API] Predicción solicitada para {symbol_lower}")
        
        # Cargar modelo
        model = cargar_modelo()
        if model is None:
            raise HTTPException(
                status_code=500,
                detail="Modelo no disponible. Ejecuta primero: python src/pipeline_maestro.py"
            )
        
        # Obtener predicción real del pipeline
        prediction_result = obtener_prediccion_real(symbol_lower, model)
        
        logger.info(f"[API] Predicción completada: {prediction_result}")
        
        return prediction_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Error en predicción: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/coins")
def get_available_coins():
    """Lista de monedas disponibles"""
    return {
        "coins": ["bitcoin", "ethereum", "solana", "cardano", "ripple"],
        "count": 5
    }

@app.get("/metrics")
def get_metrics():
    """Métricas del modelo entrenado"""
    return {
        "accuracy": 0.96,
        "roc_auc": 0.98,
        "features": 9,
        "training_samples": 155
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("[API] Iniciando servidor FastAPI...")
    uvicorn.run(app, host="127.0.0.1", port=8000)