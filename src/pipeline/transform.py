# src/transformacion/transform.py
"""
Etapa 2: Transformación y limpieza de datos OHLCV
"""
import pandas as pd
import glob
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_pipeline import RAW_DIR, PROCESSED_DIR, PROCESSED_DATA_FILE
from logging_config import setup_logging

logger = setup_logging(__name__)

NUMERIC_COLS = ["open_price", "high_price", "low_price", "close_price", "volume"]


def procesar_datos() -> pd.DataFrame | None:
    """Lee los datos raw, aplica limpieza de tipos y guarda en processed."""
    logger.info("[TRANSFORMACION] Iniciando transformación de datos...")

    try:
        # 1. Cargar archivos Parquet de la carpeta raw
        archivos = glob.glob(str(RAW_DIR / "*.parquet"))
        if not archivos:
            logger.error("[TRANSFORMACION] No hay archivos en carpeta raw")
            return None

        logger.info(f"[TRANSFORMACION] Leyendo {len(archivos)} archivo(s)")
        df = pd.concat([pd.read_parquet(f) for f in archivos], ignore_index=True)
        logger.info(f"[TRANSFORMACION] Filas cargadas: {len(df)}")
        logger.info(f"[TRANSFORMACION] Columnas: {list(df.columns)}")

        # 2. Conversión de tipos numéricos (vienen como str desde Binance)
        logger.info("[TRANSFORMACION] Convirtiendo columnas numéricas a float64...")
        for col in NUMERIC_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

        # 3. Conversión de close_time a datetime
        if "close_time" in df.columns:
            df["close_time"] = pd.to_datetime(df["close_time"], errors="coerce", unit="ms")

        # 4. Asegurar tipo temporal en open_time
        df["open_time"] = pd.to_datetime(df["open_time"], errors="coerce")

        # 5. Eliminar duplicados
        logger.info("[TRANSFORMACION] Eliminando duplicados...")
        df = df.drop_duplicates(subset=["crypto", "open_time"], keep="last")

        # 6. Eliminar nulos en columnas críticas
        logger.info("[TRANSFORMACION] Eliminando nulos en columnas críticas...")
        df = df.dropna(subset=["open_price", "close_price", "volume"])

        # 7. Añadir metadato de procesamiento y ordenar
        df["processed_at"] = datetime.now().isoformat()
        df = df.sort_values(["crypto", "open_time"]).reset_index(drop=True)

        # 8. Seleccionar columnas finales en orden canónico
        columnas_finales = [
            "crypto", "open_time", "open_price", "high_price", "low_price",
            "close_price", "volume", "close_time", "market_cap", "processed_at",
        ]
        df = df[[col for col in columnas_finales if col in df.columns]]

        # 9. Guardar como Parquet (lo leerá Spark en build_dataset)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        df.to_parquet(PROCESSED_DATA_FILE, engine="pyarrow", index=False)

        logger.info("[TRANSFORMACION] Transformación completada ✅")
        logger.info(f"[TRANSFORMACION] Shape final: {df.shape}")
        logger.info(f"[TRANSFORMACION] Guardado en: {PROCESSED_DATA_FILE}")
        logger.info(f"[TRANSFORMACION] Primeras filas:\n{df.head()}")

        return df

    except Exception as e:
        logger.error(f"[TRANSFORMACION] Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    procesar_datos()