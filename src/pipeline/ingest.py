# src/data_pipeline_Clau/ingest.py
"""
Etapa 1: Ingesta de datos desde Binance API (OHLCV horario) + CoinGecko (market cap)
"""
import requests
import time
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_pipeline import RAW_DIR, RAW_DATA_FILE, COINS
from logging_config import setup_logging

logger = setup_logging(__name__)

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

CRYPTOS = [
    {"name": "Bitcoin",     "binance": "BTCUSDT", "coingecko": "bitcoin"},
    {"name": "Ethereum",    "binance": "ETHUSDT", "coingecko": "ethereum"},
    {"name": "Solana",      "binance": "SOLUSDT", "coingecko": "solana"},
    {"name": "BinanceCoin", "binance": "BNBUSDT", "coingecko": "binancecoin"},
    {"name": "Ripple",      "binance": "XRPUSDT", "coingecko": "ripple"},
]

BINANCE_URL   = "https://api.binance.com/api/v3/klines"
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"
DAYS          = 365

# ---------------------------------------------------------------------------
# Helpers de extracción
# ---------------------------------------------------------------------------

def _extract_binance(symbol: str, start_ms: int, end_ms: int, interval: str = "1h") -> pd.DataFrame:
    """Descarga velas OHLCV de Binance con paginación automática."""
    all_rows = []
    current_start = start_ms

    while current_start < end_ms:
        params = {
            "symbol":    symbol,
            "interval":  interval,
            "startTime": current_start,
            "endTime":   end_ms,
            "limit":     1000,
        }
        response = requests.get(BINANCE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        all_rows.extend(data)
        current_start = data[-1][0] + 1  # siguiente batch
        time.sleep(0.2)

    df = pd.DataFrame(all_rows, columns=[
        "open_time", "open_price", "high_price", "low_price",
        "close_price", "volume", "close_time",
        "quote_asset_volume", "number_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "unused_field",
    ])
    df = df[["open_time", "open_price", "high_price", "low_price",
             "close_price", "volume", "close_time"]]
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    return df


def _extract_coingecko(coin_id: str, days: int = DAYS) -> pd.DataFrame:
    """Descarga market cap de CoinGecko y lo resamplea a 1h."""
    url = COINGECKO_URL.format(id=coin_id)
    params = {"vs_currency": "usd", "days": days}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data["market_caps"], columns=["open_time", "market_cap"])
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df = df.set_index("open_time").sort_index()
    df = df.resample("1h").ffill()
    return df


def _align_and_merge(df_binance: pd.DataFrame, df_coingecko: pd.DataFrame) -> pd.DataFrame:
    """Recorta ambos datasets al rango común y los une."""
    start = max(df_binance["open_time"].min(), df_coingecko.index.min())
    end   = min(df_binance["open_time"].max(), df_coingecko.index.max())

    df_binance   = df_binance[
        (df_binance["open_time"] >= start) &
        (df_binance["open_time"] <= end)
    ]
    df_coingecko = df_coingecko.loc[start:end]

    df_merged = df_binance.merge(
        df_coingecko,
        left_on="open_time",
        right_index=True,
        how="left"
    )
    return df_merged

# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------

def descargar_datos() -> pd.DataFrame:
    """Descarga y combina OHLCV (Binance) + market cap (CoinGecko) para todas las cryptos."""
    logger.info("[INGESTA] Iniciando descarga de datos...")

    start_ms = int((datetime.now() - timedelta(days=DAYS)).timestamp() * 1000)
    end_ms   = int(datetime.now().timestamp() * 1000)

    all_dfs = []

    for crypto in CRYPTOS:
        name     = crypto["name"]
        b_symbol = crypto["binance"]
        cg_id    = crypto["coingecko"]

        logger.info(f"[INGESTA] Procesando {name}...")

        try:
            df_binance   = _extract_binance(b_symbol, start_ms, end_ms)
            df_coingecko = _extract_coingecko(cg_id)
            df_merged    = _align_and_merge(df_binance, df_coingecko)

            df_merged.insert(0, "crypto", name)
            all_dfs.append(df_merged)

            logger.info(f"[INGESTA] {name} OK — {len(df_merged)} filas")

        except Exception as e:
            logger.error(f"[INGESTA] Error procesando {name}: {e}")
            raise

    df_final = pd.concat(all_dfs, ignore_index=True)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df_final.to_parquet(RAW_DATA_FILE, engine="pyarrow", index=False)

    logger.info(f"[INGESTA] Total filas: {len(df_final)}")
    logger.info(f"[INGESTA] Columnas: {list(df_final.columns)}")
    logger.info(f"[INGESTA] Rango fechas: {df_final['open_time'].min()} → {df_final['open_time'].max()}")
    logger.info(f"[INGESTA] Guardado en: {RAW_DATA_FILE}")

    return df_final


if __name__ == "__main__":
    descargar_datos()