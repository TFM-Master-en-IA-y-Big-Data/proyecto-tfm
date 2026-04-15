# src/feature_engineering/build_dataset.py
"""
Etapa 3: Feature Engineering
"""
import pandas as pd
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_pipeline import PROCESSED_DATA_FILE, DATASET_FEATURES_FILE, TARGET
from logging_config import setup_logging

logger = setup_logging(__name__)

def compute_features(df):
    """Genera features tecnicos"""
    logger.info("[FEATURES] Generando features...")
    
    # Ordenar correctamente
    df = df.sort_values(["coin", "timestamp"])

    # =========================
    # CAMBIOS PORCENTUALES
    # =========================
    df["change_1h_pct"] = df.groupby("coin")["price_usd"].pct_change(1) * 100
    df["change_24h_pct"] = df.groupby("coin")["price_usd"].pct_change(1) * 100
    df["change_7d_pct"] = df.groupby("coin")["price_usd"].pct_change(7) * 100

    # =========================
    # RSI (14)
    # =========================
    try:
        delta = df.groupby("coin")["price_usd"].diff()
        gain = (delta.where(delta > 0, 0)).groupby(df["coin"]).rolling(14).mean().reset_index(level=0, drop=True)
        loss = (-delta.where(delta < 0, 0)).groupby(df["coin"]).rolling(14).mean().reset_index(level=0, drop=True)
        rs = gain / loss
        df["rsi_14"] = 100 - (100 / (1 + rs))
    except:
        logger.warning("[FEATURES] No se pudo calcular RSI, usando valores por defecto")
        df["rsi_14"] = 50.0

    # =========================
    # VOLATILIDAD (30 dias)
    # =========================
    try:
        df["volatility_30d"] = df.groupby("coin")["price_usd"].rolling(30).std().reset_index(level=0, drop=True)
    except:
        logger.warning("[FEATURES] No se pudo calcular volatilidad, usando valores por defecto")
        df["volatility_30d"] = 0.1

    # =========================
    # MEDIAS MOVILES
    # =========================
    try:
        df["price_sma_7"] = df.groupby("coin")["price_usd"].rolling(7).mean().reset_index(level=0, drop=True)
        df["price_sma_30"] = df.groupby("coin")["price_usd"].rolling(30).mean().reset_index(level=0, drop=True)
    except:
        logger.warning("[FEATURES] No se pudo calcular SMA, usando valores por defecto")
        df["price_sma_7"] = df["price_usd"]
        df["price_sma_30"] = df["price_usd"]

    return df


def build_dataset():
    """Construye dataset con features"""
    logger.info("[FEATURES] Construyendo dataset con features...")
    
    try:
        # Lee datos ya limpios
        df = pd.read_csv(PROCESSED_DATA_FILE)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        logger.info(f"[FEATURES] Cargados {len(df)} registros")
        
        # =========================
        # FEATURE ENGINEERING
        # =========================
        df = compute_features(df)

        # =========================
        # TARGET (sube/baja)
        # =========================
        df["target"] = (df["change_24h_pct"] > 0).astype(int)

        # =========================
        # LIMPIEZA FINAL - SIN DROPNA
        # ✅ CAMBIO CLAVE: Rellenar todos los NaN con metodos seguros
        # =========================
        logger.info(f"[FEATURES] Filas ANTES de rellenar: {len(df)}")
        logger.info(f"[FEATURES] NaNs por columna ANTES:\n{df.isna().sum()}")
        
        # Rellenar valores infinitos con NaN
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Rellenar hacia adelante y hacia atras
        df = df.bfill().ffill()
        
        # Si quedan NaN, rellenar con media de la columna
        for col in df.columns:
            if df[col].isna().any():
                media = df[col].mean()
                if pd.isna(media):
                    media = 0
                df[col] = df[col].fillna(media)
        
        logger.info(f"[FEATURES] Filas DESPUES de rellenar: {len(df)}")
        logger.info(f"[FEATURES] NaNs por columna DESPUES:\n{df.isna().sum()}")

        # =========================
        # GUARDAR DATASET
        # =========================
        df.to_csv(DATASET_FEATURES_FILE, index=False)

        logger.info("[FEATURES] Dataset con features generado")
        logger.info(f"[FEATURES] Guardado en: {DATASET_FEATURES_FILE}")
        logger.info(f"[FEATURES] Shape final: {df.shape}")
        logger.info(f"[FEATURES] Primeras filas:\n{df.head()}")
        
        return df

    except Exception as e:
        logger.error(f"[FEATURES] Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    build_dataset()