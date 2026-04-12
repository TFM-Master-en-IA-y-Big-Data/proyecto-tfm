# =========================
# CONFIGURACIÓN DEL PROYECTO
# =========================

# Features del modelo
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

# Variable objetivo
TARGET = "target"

# Paths
DATA_PATH = "../data/dataset.csv"
RAW_DATA_PATH = "../data/raw_data.csv"
MODEL_PATH = "../models/model.pkl"

# Criptomonedas a usar (puedes ampliar)
COINS = [
    "bitcoin",
    "ethereum",
    "solana",
    "cardano",
    "ripple"
]

# Parámetros del modelo
MODEL_PARAMS = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "eval_metric": "logloss"
}