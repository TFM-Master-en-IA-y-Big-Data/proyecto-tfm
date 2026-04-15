# src/data_pipeline_Clau/ingest.py
"""
Etapa 1: Ingesta de datos desde CoinGecko API
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_pipeline import RAW_DIR, RAW_DATA_FILE, COINS
from logging_config import setup_logging

logger = setup_logging(__name__)

def descargar_datos():
    """Descarga datos históricos de CoinGecko API"""
    logger.info("[INGESTA] Iniciando descarga de datos...")
    
    # Usar endpoint de histórico en lugar de simple/price
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    
    params = {
        'vs_currency': 'usd',
        'days': '30',  # Últimos 30 días para tener histórico
        'interval': 'daily'
    }
    
    try:
        logger.info(f"[INGESTA] Descargando datos históricos de últimos 30 días...")
        
        all_data = []
        
        for coin in COINS:
            logger.info(f"[INGESTA] Descargando {coin}...")
            
            params['vs_currency'] = 'usd'
            url_coin = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
            
            response = requests.get(url_coin, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            prices = data.get("prices", [])
            volumes = data.get("total_volumes", [])
            market_caps = data.get("market_caps", [])
            
            for i in range(len(prices)):
                all_data.append({
                    'coin_id': coin,
                    'timestamp': datetime.fromtimestamp(prices[i][0] / 1000),
                    'price_usd': prices[i][1],
                    'volume_24h': volumes[i][1] if i < len(volumes) else 0,
                    'market_cap': market_caps[i][1] if i < len(market_caps) else 0,
                })
        
        df = pd.DataFrame(all_data)
        
        logger.info(f"[INGESTA] Datos descargados: {len(df)} registros de {len(COINS)} monedas")
        
        # Guardar en Parquet
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        df.to_parquet(RAW_DATA_FILE, engine='pyarrow', index=False)
        
        logger.info(f"[INGESTA] Guardado en: {RAW_DATA_FILE}")
        logger.info(f"[INGESTA] Columnas: {list(df.columns)}")
        logger.info(f"[INGESTA] Rango de fechas: {df['timestamp'].min()} a {df['timestamp'].max()}")
        
        return df
        
    except Exception as e:
        logger.error(f"[INGESTA] Error: {e}")
        raise

if __name__ == "__main__":
    descargar_datos()