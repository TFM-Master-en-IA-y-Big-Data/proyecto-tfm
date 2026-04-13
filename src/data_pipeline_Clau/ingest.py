import requests
import pandas as pd
import os
from datetime import datetime

def descargar_datos():
    """
    Función de Ingesta: Conecta con la API de CoinGecko, extrae precios 
    de BTC/ETH y los almacena en bruto (formato Parquet) en el Data Lake.
    """
    print("🚀 Iniciando ingesta de datos...")
    
    # Configuración de la API: IDs de las monedas y parámetros requeridos
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin,ethereum',
        'vs_currencies': 'usd',
        'include_24hr_vol': 'true',
        'include_last_updated_at': 'true'
    }
    
    try:
        # Petición a la API externa
        response = requests.get(url, params=params)
        response.raise_for_status() # Verifica si la respuesta es 200 (OK)
        data = response.json()
        
        # --- PROCESAMIENTO INICIAL ---
        # Convertimos el diccionario JSON a un DataFrame de Pandas
        # .transpose() se usa porque CoinGecko devuelve las monedas como columnas
        df = pd.DataFrame(data).transpose()
        df.index.name = 'coin_id'
        df = df.reset_index()
        
        # Limpieza de tipos: Aseguramos que los textos sean strings puros
        # Esto evita errores de compatibilidad al guardar en formato Parquet
        df['coin_id'] = df['coin_id'].astype(str)
        df['fetch_timestamp'] = str(datetime.now().isoformat())
        
        # --- ALMACENAMIENTO (DATA LAKE) ---
        # Creamos la ruta 'data/raw' si no existe (almacenamiento persistente local)
        os.makedirs("data/raw", exist_ok=True)
        
        # Generamos un nombre único basado en el tiempo para evitar sobrescribir datos
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        ruta_archivo = f"data/raw/crypto_data_{timestamp_str}.parquet"
        
        # Guardamos usando 'pyarrow' por ser más eficiente y estable con Big Data
        df.to_parquet(ruta_archivo, engine='pyarrow', index=False)
        
        print(f"✅ ¡Éxito! Archivo guardado en: {ruta_archivo}")
        print("-" * 30)
        print(df[['coin_id', 'usd', 'usd_24h_vol']])
        print("-" * 30)
        
    except Exception as e:
        # Gestión de errores: si la API cae o falla el guardado, lo reportamos
        print(f"❌ Error durante la ingesta: {e}")

# Punto de entrada del script
if __name__ == "__main__":
    descargar_datos()
