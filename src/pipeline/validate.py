# src/transformacion/validate.py
"""
Etapa 2.5: Validación de calidad de datos
"""
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_pipeline import PROCESSED_DATA_FILE
from logging_config import setup_logging

logger = setup_logging(__name__)

def validar_dataset():
    """Validaciones críticas antes de ML"""
    logger.info("[VALIDACION] Validando dataset...")
    
    if not PROCESSED_DATA_FILE.exists():
        logger.error(f"[VALIDACION] Archivo no encontrado: {PROCESSED_DATA_FILE}")
        return False
    
    try:
        df = pd.read_csv(PROCESSED_DATA_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        validaciones = {
            "Dataset no vacio": len(df) > 0,
            "Sin duplicados": df.duplicated().sum() == 0,
            "Columna 'coin' existe": 'coin' in df.columns,
            "Columna 'price_usd' existe": 'price_usd' in df.columns,
            "Sin nulos en precios": df['price_usd'].notna().all(),
            "Sin nulos en volumen": df['volume_24h'].notna().all(),
            "Datos recientes (< 7 dias)": (datetime.now() - df['timestamp'].max()).days < 7,
            "Monedas suficientes (>= 3)": len(df['coin'].unique()) >= 3,
            "Precios > 0": (df['price_usd'] > 0).all(),
        }
        
        todos_ok = True
        for check, resultado in validaciones.items():
            status = "[OK]" if resultado else "[FAIL]"
            logger.info(f"{status} {check}")
            if not resultado:
                todos_ok = False
        
        if todos_ok:
            logger.info("[VALIDACION] Todas las validaciones pasaron")
        else:
            logger.warning("[VALIDACION] Algunas validaciones fallaron")
        
        return todos_ok
        
    except Exception as e:
        logger.error(f"[VALIDACION] Error: {e}")
        return False

if __name__ == "__main__":
    validar_dataset()