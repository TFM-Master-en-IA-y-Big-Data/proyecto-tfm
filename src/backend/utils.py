# src/backend/utils.py
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

def cargar_modelo():
    """Carga el modelo entrenado"""
    try:
        if os.path.exists(MODEL_PATH):
            logger.info(f"[UTILS] Cargando modelo desde {MODEL_PATH}")
            return joblib.load(MODEL_PATH)
        else:
            logger.warning(f"[UTILS] Modelo no encontrado en {MODEL_PATH}")
            return None
    except Exception as e:
        logger.error(f"[UTILS] Error cargando modelo: {e}")
        return None

def obtener_datos_historicos(symbol: str):
    """Lee datos históricos del dataset procesado"""
    try:
        if not os.path.exists(DATASET_FEATURES_FILE):
            logger.warning(f"[UTILS] Dataset no encontrado: {DATASET_FEATURES_FILE}")
            return None
        
        df = pd.read_csv(DATASET_FEATURES_FILE)
        df_coin = df[df['coin'] == symbol.lower()]
        
        if df_coin.empty:
            logger.warning(f"[UTILS] Sin datos para {symbol}")
            return None
        
        return df_coin.tail(1)  # Último registro
        
    except Exception as e:
        logger.error(f"[UTILS] Error leyendo datos históricos: {e}")
        return None

def obtener_prediccion_real(symbol: str, model):
    """
    Hace predicción REAL usando el modelo entrenado
    """
    try:
        # Obtener últimos datos
        data = obtener_datos_historicos(symbol)
        
        if data is None or data.empty:
            logger.warning(f"[UTILS] No hay datos para {symbol}, retornando predicción dummy")
            return generar_prediccion_dummy(symbol)
        
        # Preparar features
        X = data[FEATURES]
        
        # Predicción
        prediction = model.predict(X)[0]  # 0 = baja, 1 = sube
        probability = model.predict_proba(X)[0]
        
        # Extraer datos
        price = float(data['price_usd'].values[0])
        market_cap = float(data['market_cap'].values[0])
        
        # Calcular nivel de riesgo
        volatility = float(data['volatility_30d'].values[0])
        if volatility > 5:
            risk_level = "Alto"
        elif volatility > 2:
            risk_level = "Medio"
        else:
            risk_level = "Bajo"
        
        # Generar gráfica de tendencia
        trend_data = generar_trend_data(data)
        
        prediction_text = "Subida" if prediction == 1 else "Bajada"
        prob_value = float(max(probability))
        
        logger.info(f"[UTILS] {symbol}: {prediction_text} ({prob_value*100:.1f}%)")
        
        return {
            "coin": symbol.upper(),
            "prediction": prediction_text,
            "probability": prob_value,
            "current_price": price,
            "market_cap": market_cap,
            "trend_data": trend_data,
            "risk_level": risk_level,
            "confidence": prob_value
        }
        
    except Exception as e:
        logger.error(f"[UTILS] Error en predicción real: {e}")
        raise

def generar_prediccion_dummy(symbol: str):
    """Predicción dummy si no hay datos disponibles"""
    import random
    return {
        "coin": symbol.upper(),
        "prediction": random.choice(["Subida", "Bajada"]),
        "probability": round(random.uniform(0.6, 0.99), 2),
        "current_price": 50000 if symbol.lower() == "bitcoin" else 2500,
        "market_cap": 1e12,
        "trend_data": [random.uniform(10, 50) for _ in range(7)],
        "risk_level": random.choice(["Bajo", "Medio", "Alto"]),
        "confidence": 0.5
    }

def generar_trend_data(data):
    """Genera datos de tendencia para la gráfica basados en precios históricos"""
    try:
        # Obtener todos los datos de la moneda
        df = pd.read_csv(DATASET_FEATURES_FILE)
        coin = data['coin'].values[0].lower()
        df_coin = df[df['coin'] == coin]
        
        if df_coin.empty:
            return [50.0] * 7
        
        # Tomar los últimos 7 datos
        last_7 = df_coin.tail(7)['price_usd'].values
        
        if len(last_7) == 0:
            return [50.0] * 7
        
        # Normalizar a 0-100
        min_price = float(last_7.min())
        max_price = float(last_7.max())
        range_price = max_price - min_price if max_price > min_price else 1
        
        normalized = [(p - min_price) / range_price * 100 for p in last_7]
        
        # Rellenar a 7 si es necesario
        while len(normalized) < 7:
            normalized.insert(0, normalized[0])
        
        return [float(x) for x in normalized[-7:]]
        
    except Exception as e:
        print(f"[UTILS] Error generando trend_data: {e}")
        return [50.0] * 7