# src/transformacion/validate.py
"""
Etapa 2.5: Validación de calidad de datos OHLCV
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_pipeline import PROCESSED_DATA_FILE
from logging_config import setup_logging

logger = setup_logging(__name__)


def validar_dataset() -> bool:
    """Validaciones críticas del dataset procesado antes del feature engineering."""
    logger.info("[VALIDACION] Validando dataset...")

    if not PROCESSED_DATA_FILE.exists():
        logger.error(f"[VALIDACION] Archivo no encontrado: {PROCESSED_DATA_FILE}")
        return False

    try:
        df = pd.read_parquet(PROCESSED_DATA_FILE)

        validaciones = {
            # Estructura básica
            "Dataset no vacío":                    len(df) > 0,
            "Sin duplicados (crypto + open_time)": not df.duplicated(subset=["crypto", "open_time"]).any(),
            # Columnas OHLCV presentes
            "Columna 'crypto' existe":             "crypto"      in df.columns,
            "Columna 'open_time' existe":          "open_time"   in df.columns,
            "Columna 'open_price' existe":         "open_price"  in df.columns,
            "Columna 'high_price' existe":         "high_price"  in df.columns,
            "Columna 'low_price' existe":          "low_price"   in df.columns,
            "Columna 'close_price' existe":        "close_price" in df.columns,
            "Columna 'volume' existe":             "volume"      in df.columns,
            "Columna 'close_time' existe":         "close_time"  in df.columns,
            "Columna 'market_cap' existe":         "market_cap"  in df.columns,
            # Calidad de datos
            "Sin nulos en open_price":             df["open_price"].notna().all(),
            "Sin nulos en close_price":            df["close_price"].notna().all(),
            "Sin nulos en volume":                 df["volume"].notna().all(),
            "Precios > 0":                         (df["open_price"] > 0).all(),
            "Volumen >= 0":                        (df["volume"] >= 0).all(),
            "high_price >= low_price":             (df["high_price"] >= df["low_price"]).all(),
            # Cobertura temporal
            "Datos recientes (< 7 días)":          (datetime.now() - pd.to_datetime(df["open_time"]).max()).days < 7,
            # Cobertura de activos
            "Exactamente 5 cryptos":               df["crypto"].nunique() == 5,
            "Filas por crypto uniformes":          df["crypto"].value_counts().std() < 100,
        }

        todos_ok = True
        for check, resultado in validaciones.items():
            status = "[OK]  " if resultado else "[FAIL]"
            logger.info(f"{status} {check}")
            if not resultado:
                todos_ok = False

        if todos_ok:
            logger.info("[VALIDACION] ✅ Todas las validaciones pasaron")
        else:
            logger.warning("[VALIDACION] ⚠️  Algunas validaciones fallaron")

        return todos_ok

    except Exception as e:
        logger.error(f"[VALIDACION] Error: {e}")
        return False


if __name__ == "__main__":
    validar_dataset()