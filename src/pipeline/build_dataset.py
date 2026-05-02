# src/feature_engineering/build_dataset.py
"""
Etapa 3: Feature Engineering con Apache Spark (procesamiento distribuido)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_pipeline import PROCESSED_DATA_FILE, DATASET_FEATURES_FILE
from logging_config import setup_logging

logger = setup_logging(__name__)


def _init_spark():
    """Inicializa SparkSession en modo local."""
    try:
        import findspark
        findspark.init()
    except ImportError:
        logger.warning("[FEATURES] findspark no disponible, asumiendo Spark en PATH")

    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder
        .master("local[*]")
        .appName("MotorProcesamientoCriptomonedas")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    logger.info(f"[FEATURES] SparkSession iniciada — versión {spark.version}")
    return spark


def compute_features(df):
    """
    Genera features técnicos mediante window functions de Spark.

    Columnas de entrada (Data Lake OHLCV):
        crypto, open_time, open_price, high_price, low_price,
        close_price, volume, close_time, market_cap

    Columnas de salida (dataset ML):
        crypto, timestamp, price_usd, market_cap,
        change_1h_pct, change_24h_pct, change_7d_pct,
        volatility_30d, rsi_14, volume_24h,
        crypto_encoded, hour, day_of_week, month
    """
    from pyspark.sql.functions import (
        col, lag, when, avg, stddev, sum as spark_sum,
        hour, dayofweek, month, dense_rank
    )
    from pyspark.sql.window import Window

    # ------------------------------------------------------------------
    # Eliminar columnas irrelevantes para ML
    # ------------------------------------------------------------------
    logger.info("[FEATURES] Eliminando columnas irrelevantes...")
    df = df.drop("open_price", "high_price", "low_price", "close_time")

    # ------------------------------------------------------------------
    # Definición de ventanas temporales
    # ------------------------------------------------------------------
    w     = Window.partitionBy("crypto").orderBy("open_time")
    w_14  = Window.partitionBy("crypto").orderBy("open_time").rowsBetween(-13,  0)
    w_24h = Window.partitionBy("crypto").orderBy("open_time").rowsBetween(-23,  0)
    w_30d = Window.partitionBy("crypto").orderBy("open_time").rowsBetween(-719, 0)

    # ------------------------------------------------------------------
    # Variaciones porcentuales
    # ------------------------------------------------------------------
    logger.info("[FEATURES] Calculando variaciones porcentuales...")

    prev_1h  = lag("close_price", 1).over(w)
    prev_24h = lag("close_price", 24).over(w)
    prev_7d  = lag("close_price", 168).over(w)

    df = df.withColumn("change_1h_pct",
        (col("close_price") - prev_1h) / prev_1h * 100
    )
    df = df.withColumn("change_24h_pct",
        (col("close_price") - prev_24h) / prev_24h * 100
    )
    df = df.withColumn("change_7d_pct",
        (col("close_price") - prev_7d) / prev_7d * 100
    )

    # ------------------------------------------------------------------
    # Volatilidad 30 días (std sobre ventana de 720 velas horarias)
    # ------------------------------------------------------------------
    logger.info("[FEATURES] Calculando volatilidad 30d...")
    df = df.withColumn("volatility_30d", stddev("close_price").over(w_30d))

    # ------------------------------------------------------------------
    # RSI 14
    # ------------------------------------------------------------------
    logger.info("[FEATURES] Calculando RSI 14...")
    df = df.withColumn("price_diff",
        col("close_price") - lag("close_price", 1).over(w)
    )
    df = df.withColumn("gain",
        when(col("price_diff") > 0,  col("price_diff")).otherwise(0)
    )
    df = df.withColumn("loss",
        when(col("price_diff") < 0, -col("price_diff")).otherwise(0)
    )
    df = df.withColumn("avg_gain", avg("gain").over(w_14))
    df = df.withColumn("avg_loss", avg("loss").over(w_14))
    df = df.withColumn("rsi_14",
        when(col("avg_loss") == 0, 100.0)
        .otherwise(100.0 - (100.0 / (1.0 + col("avg_gain") / col("avg_loss"))))
    )

    # ------------------------------------------------------------------
    # Volumen acumulado 24h
    # ------------------------------------------------------------------
    logger.info("[FEATURES] Calculando volumen acumulado 24h...")
    df = df.withColumn("volume_24h", spark_sum("volume").over(w_24h))

    # ------------------------------------------------------------------
    # Features temporales extraídas de open_time
    # ------------------------------------------------------------------
    logger.info("[FEATURES] Extrayendo features temporales...")
    df = df.withColumn("hour",        hour("open_time"))
    df = df.withColumn("day_of_week", dayofweek("open_time"))
    df = df.withColumn("month",       month("open_time"))

    # ------------------------------------------------------------------
    # Codificación numérica de crypto (label encoding con dense_rank)
    # ------------------------------------------------------------------
    logger.info("[FEATURES] Codificando columna 'crypto'...")
    w_global = Window.orderBy("crypto")
    df = df.withColumn("crypto_encoded", dense_rank().over(w_global) - 1)

    # ------------------------------------------------------------------
    # Limpieza de columnas intermedias del cálculo RSI
    # ------------------------------------------------------------------
    df = df.drop("volume", "price_diff", "gain", "loss", "avg_gain", "avg_loss")

    # ------------------------------------------------------------------
    # Renombrado final para alinear con el modelo de datos del proyecto
    # ------------------------------------------------------------------
    df = df.withColumnRenamed("open_time",   "timestamp")
    df = df.withColumnRenamed("close_price", "price_usd")

    # ------------------------------------------------------------------
    # Orden canónico de columnas del dataset final
    # ------------------------------------------------------------------
    columnas_finales = [
        "crypto", "timestamp",
        "price_usd", "market_cap",
        "change_1h_pct", "change_24h_pct", "change_7d_pct",
        "volatility_30d", "rsi_14", "volume_24h",
        "crypto_encoded", "hour", "day_of_week", "month",
    ]
    df = df.select(columnas_finales)

    return df


def build_dataset():
    """Orquesta la carga, feature engineering y almacenamiento del dataset ML final."""
    logger.info("[FEATURES] Construyendo dataset con features...")

    spark = _init_spark()

    try:
        # ------------------------------------------------------------------
        # 1. Carga del Parquet generado por transform.py
        # ------------------------------------------------------------------
        input_path = str(PROCESSED_DATA_FILE)
        logger.info(f"[FEATURES] Leyendo: {input_path}")

        df = spark.read.parquet(input_path)

        logger.info(f"[FEATURES] Filas cargadas: {df.count()}")
        logger.info("[FEATURES] Schema de entrada:")
        df.printSchema()

        # ------------------------------------------------------------------
        # 2. Feature engineering distribuido
        # ------------------------------------------------------------------
        df = compute_features(df)

        logger.info("[FEATURES] Schema final:")
        df.printSchema()
        df.show(10, truncate=False)

        # ------------------------------------------------------------------
        # 3. Almacenamiento como Parquet optimizado para ML
        #    toPandas() → único fichero, igual que el notebook
        # ------------------------------------------------------------------
        output_path = str(DATASET_FEATURES_FILE)
        DATASET_FEATURES_FILE.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"[FEATURES] Guardando en: {output_path}")
        df.toPandas().to_parquet(output_path, index=False, engine="pyarrow")

        logger.info("[FEATURES] ✅ Dataset ML almacenado correctamente")
        logger.info(f"[FEATURES] Ruta: {output_path}")

        return df

    except Exception as e:
        logger.error(f"[FEATURES] Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

    finally:
        spark.stop()
        logger.info("[FEATURES] SparkSession cerrada")


if __name__ == "__main__":
    build_dataset()