# src/config_pipeline.py
"""
Configuración centralizada del pipeline
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Directorios
# ---------------------------------------------------------------------------
BASE_DIR      = Path(__file__).parent.parent
DATA_DIR      = BASE_DIR / "data"
RAW_DIR       = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed" / "data_lake"
MODELS_DIR    = DATA_DIR / "models"
OUTPUTS_DIR   = BASE_DIR / "outputs"

# Crear carpetas si no existen
for dir_path in [RAW_DIR, PROCESSED_DIR, MODELS_DIR, OUTPUTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Archivos
# ---------------------------------------------------------------------------
RAW_DATA_FILE         = RAW_DIR       / "raw_cryptos.parquet"
PROCESSED_DATA_FILE   = PROCESSED_DIR / "all_cryptos.parquet"
DATASET_FEATURES_FILE = DATA_DIR / "ml" / "features" / "all_cryptos_ml.parquet"
MODEL_PATH            = MODELS_DIR / "model.pkl"

# Crear carpeta ml/features si no existe
(DATA_DIR / "ml" / "features").mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Monedas
# crypto_encoded (generado por dense_rank en build_dataset.py, orden alfabético):
#   0 → binancecoin
#   1 → bitcoin
#   2 → ethereum
#   3 → ripple
#   4 → solana
# ---------------------------------------------------------------------------
COINS = [
    "bitcoin",
    "ethereum",
    "solana",
    "binancecoin",
    "ripple",
]

# ---------------------------------------------------------------------------
# Columnas identificadoras (no entran al modelo directamente)
# ---------------------------------------------------------------------------
ID_COLS = ["crypto", "timestamp"]

# ---------------------------------------------------------------------------
# Features que entran al modelo
# crypto_encoded y las temporales se generan en build_dataset.py
# ---------------------------------------------------------------------------
FEATURES = [
    "market_cap",
    "change_1h_pct",
    "change_24h_pct",
    "change_7d_pct",
    "volatility_30d",
    "rsi_14",
    "volume_24h",
    "crypto_encoded",
    "hour",
    "day_of_week",
    "month",
]

# ---------------------------------------------------------------------------
# Target — se definirá concretamente en la fase de ML
# ---------------------------------------------------------------------------
TARGET = "price_usd"

# ---------------------------------------------------------------------------
# Parámetros generales
# ---------------------------------------------------------------------------
DAYS_HISTORICAL   = 365
N_MONEDAS_MONITOR = 100
VERBOSE           = True
LOG_LEVEL         = "INFO"
STRICT_FEATURES = True