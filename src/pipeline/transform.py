# src/transformacion/transform.py
"""
Etapa 2: Transformación y limpieza de datos
"""
import pandas as pd
import os
import glob
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_pipeline import RAW_DIR, PROCESSED_DIR, PROCESSED_DATA_FILE
from logging_config import setup_logging

logger = setup_logging(__name__)

def procesar_datos():
    """
    Transformación: Lee Raw -> Limpia -> Guarda en Processed
    """
    logger.info("[TRANSFORMACION] Iniciando transformacion de datos...")
    
    try:
        # 1. Buscar archivos Parquet
        path_pattern = str(RAW_DIR / "*.parquet")
        archivos = glob.glob(path_pattern)
        
        if not archivos:
            logger.error("[TRANSFORMACION] No hay archivos en carpeta raw")
            return None
        
        logger.info(f"[TRANSFORMACION] Leyendo {len(archivos)} archivos")
        
        # 2. Cargar y combinar
        lista_df = [pd.read_parquet(f) for f in archivos]
        df_unido = pd.concat(lista_df, ignore_index=True)
        
        logger.info(f"[TRANSFORMACION] Datos combinados: {len(df_unido)} filas")
        logger.info(f"[TRANSFORMACION] Columnas encontradas: {list(df_unido.columns)}")
        
        # 3. NORMALIZACIÓN - Mapear nombres de columnas antiguos a nuevos
        columna_mapping = {
            'usd': 'price_usd',
            'usd_24h_vol': 'volume_24h',
            'usd_market_cap': 'market_cap'
        }
        
        df_unido = df_unido.rename(columns=columna_mapping)
        
        logger.info(f"[TRANSFORMACION] Columnas después de normalizar: {list(df_unido.columns)}")
        
        # 4. LIMPIEZA - Duplicados
        logger.info("[TRANSFORMACION] Limpiando duplicados...")
        df_clean = df_unido.drop_duplicates(subset=['coin_id', 'timestamp'], keep='last')
        
        logger.info("[TRANSFORMACION] Eliminando nulos...")
        df_clean = df_clean.dropna(subset=['price_usd', 'volume_24h'], how='any')
        
        # 5. NORMALIZACIÓN - Datos
        logger.info("[TRANSFORMACION] Normalizando para ML...")
        df_clean['coin'] = df_clean['coin_id'].str.lower()
        df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'])
        df_clean['processed_at'] = datetime.now().isoformat()
        
        # Ordenar como necesita Jesús
        df_clean = df_clean.sort_values(['coin', 'timestamp'])
        
        # Seleccionar solo columnas necesarias
        columnas_finales = ['coin_id', 'coin', 'timestamp', 'price_usd', 'volume_24h', 'market_cap', 'processed_at']
        df_clean = df_clean[[col for col in columnas_finales if col in df_clean.columns]]
        
        # 6. GUARDAR
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        df_clean.to_csv(PROCESSED_DATA_FILE, index=False)
        
        logger.info("[TRANSFORMACION] Transformacion completada")
        logger.info(f"[TRANSFORMACION] Guardado en: {PROCESSED_DATA_FILE}")
        logger.info(f"[TRANSFORMACION] Shape final: {df_clean.shape}")
        logger.info(f"[TRANSFORMACION] Primeras filas:\n{df_clean.head()}")
        
        return df_clean
        
    except Exception as e:
        logger.error(f"[TRANSFORMACION] Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    procesar_datos()