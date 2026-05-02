# src/backend/feature_builder.py
import pandas as pd
import numpy as np

from src.config_pipeline import FEATURES

CRYPTO_MAP = {
    "bitcoin": 1,
    "ethereum": 2,
    "solana": 4,
    "binancecoin": 0,
    "ripple": 3,
}


def build_model_input(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """
    Construye exactamente el input que espera el modelo.
    Evita dependencia de columnas inconsistentes del dataset.
    """

    df = df.copy()

    # -------------------------------------------------
    # crypto encoding fijo (CRÍTICO)
    # -------------------------------------------------
    df["crypto_encoded"] = CRYPTO_MAP.get(symbol.lower(), -1)

    # -------------------------------------------------
    # asegurar columnas faltantes
    # -------------------------------------------------
    for f in FEATURES:
        if f not in df.columns:
            df[f] = 0.0

    # -------------------------------------------------
    # limpiar NaN/inf
    # -------------------------------------------------
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0)

    return df[FEATURES]