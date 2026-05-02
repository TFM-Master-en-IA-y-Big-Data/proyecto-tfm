"""
Utilidades para cargar modelo y hacer predicciones reales
"""
import joblib
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config_pipeline import MODEL_PATH, DATASET_FEATURES_FILE, FEATURES
from src.logging_config import setup_logging

logger = setup_logging(__name__)


# ---------------------------------------------------------------------------
# MODELO
# ---------------------------------------------------------------------------
def cargar_modelo():
    try:
        if os.path.exists(MODEL_PATH):
            logger.info(f"[UTILS] Cargando modelo desde {MODEL_PATH}")
            return joblib.load(MODEL_PATH)
        else:
            logger.warning("[UTILS] Modelo no encontrado")
            return None
    except Exception as e:
        logger.error(f"[UTILS] Error cargando modelo: {e}")
        return None


# ---------------------------------------------------------------------------
# DATOS
# ---------------------------------------------------------------------------
def obtener_datos_historicos(symbol: str):
    try:
        if not os.path.exists(DATASET_FEATURES_FILE):
            logger.warning("[UTILS] Dataset no encontrado")
            return None

        df = pd.read_parquet(DATASET_FEATURES_FILE)

        # 🔥 FIX 1: normalización robusta (evita BinanceCoin vs binancecoin)
        df["crypto_norm"] = df["crypto"].str.lower()
        symbol_norm = symbol.lower()

        df_coin = df[df["crypto_norm"] == symbol_norm]

        if df_coin.empty:
            logger.warning(f"[UTILS] No hay datos para {symbol}")
            return None

        df_coin = df_coin.sort_values("timestamp")

        # 🔥 FIX 2: eliminar filas con NaN en features críticas
        df_coin = df_coin.dropna(subset=["price_usd", "crypto_encoded"])

        return df_coin.tail(1)

    except Exception as e:
        logger.error(f"[UTILS] Error leyendo datos: {e}")
        return None


# ---------------------------------------------------------------------------
# PREDICCIÓN REAL
# ---------------------------------------------------------------------------
def obtener_prediccion_real(symbol: str, model) -> dict:
    try:
        data = obtener_datos_historicos(symbol)

        if data is None:
            return generar_prediccion_dummy(symbol)

        features_disponibles = [f for f in FEATURES if f in data.columns]
        X = data[features_disponibles].copy().fillna(0)

        precio_actual = float(data["price_usd"].values[0])
        precio_predicho = float(model.predict(X)[0])

        variacion_pct = ((precio_predicho - precio_actual) / precio_actual) * 100
        prediction_text = "Subida" if variacion_pct > 0 else "Bajada"

        volatility = float(data["volatility_30d"].values[0]) if "volatility_30d" in data.columns else 0.0

        if volatility > 5:
            risk_level = "Alto"
        elif volatility > 2:
            risk_level = "Medio"
        else:
            risk_level = "Bajo"

        confidence = min(abs(variacion_pct) / 10, 1.0)

        # 🔥 OBLIGATORIO POR SCHEMA
        market_cap = float(data["market_cap"].values[0]) if "market_cap" in data.columns else 0.0
        trend_data = generar_trend_data(symbol)

        return {
            "coin": symbol.upper(),
            "prediction": prediction_text,
            "probability": round(confidence, 4),
            "current_price": precio_actual,
            "predicted_price": precio_predicho,
            "variation_pct": round(variacion_pct, 4),

            # 🔥 estos dos eran los que te estaban rompiendo todo
            "market_cap": market_cap,
            "trend_data": trend_data,

            "risk_level": risk_level,
            "confidence": round(confidence, 4),
        }

    except Exception as e:
        logger.error(f"[UTILS] Error en predicción: {e}")
        return generar_prediccion_dummy(symbol)


# ---------------------------------------------------------------------------
# FALLBACK (IMPORTANTE: NO RANDOM “MENTIROSO”)
# ---------------------------------------------------------------------------
def generar_prediccion_dummy(symbol: str) -> dict:
    """
    Fallback controlado (NO aleatorio para evitar confusión en frontend)
    """
    return {
        "coin": symbol.upper(),
        "prediction": "Sin datos suficientes",
        "probability": 0.0,
        "current_price": 0.0,
        "predicted_price": 0.0,
        "variation_pct": 0.0,
        "risk_level": "Desconocido",
        "confidence": 0.0,
    }


# ---------------------------------------------------------------------------
# TREND DATA
# ---------------------------------------------------------------------------
def generar_trend_data(symbol: str):
    try:
        df = pd.read_parquet(DATASET_FEATURES_FILE)

        df["crypto_norm"] = df["crypto"].str.lower()
        df_coin = df[df["crypto_norm"] == symbol.lower()]

        if df_coin.empty:
            return [50.0] * 7

        last_7 = df_coin["price_usd"].ffill().tail(7).tolist()

        min_p, max_p = min(last_7), max(last_7)
        rango = max_p - min_p if max_p > min_p else 1

        normalized = [(p - min_p) / rango * 100 for p in last_7]

        while len(normalized) < 7:
            normalized.insert(0, normalized[0])

        return [round(x, 2) for x in normalized[-7:]]

    except Exception as e:
        logger.error(f"[UTILS] Error trend: {e}")
        return [50.0] * 7