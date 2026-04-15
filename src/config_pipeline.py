# src/config_pipeline.py
"""
Configuración centralizada del pipeline
"""
import os
from pathlib import Path

# Directorios
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Crear carpetas si no existen
for dir_path in [RAW_DIR, PROCESSED_DIR, MODELS_DIR, OUTPUTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Archivos
RAW_DATA_FILE = RAW_DIR / "crypto_data_latest.parquet"
PROCESSED_DATA_FILE = PROCESSED_DIR / "dataset_limpio.csv"
DATASET_FEATURES_FILE = PROCESSED_DIR / "dataset_features.csv"
MODEL_PATH = MODELS_DIR / "model.pkl"

# Monedas
COINS = [
    "bitcoin",
    "ethereum",
    "solana",
    "cardano",
    "ripple"
]

# Features (del config de Jesús)
FEATURES = [
    "change_1h_pct",
    "change_24h_pct",
    "change_7d_pct",
    "volume_24h",
    "market_cap",
    "rsi_14",
    "volatility_30d",
    "price_sma_7",
    "price_sma_30"
]

TARGET = "target"

# Parámetros
DAYS_HISTORICAL = 365
N_MONEDAS_MONITOR = 100

# Pipeline
VERBOSE = True
LOG_LEVEL = "INFO"