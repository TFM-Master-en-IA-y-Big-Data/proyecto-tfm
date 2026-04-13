import pandas as pd
import os
import glob
from datetime import datetime

def procesar_datos():
    """
    Función de Transformación: Lee los datos Raw, los limpia y los
    guarda en la carpeta Processed (Capa Silver del Data Lake).
    """
    print("✨ Iniciando procesamiento de datos (Pandas Engine)...")
    
    path_raw = "data/raw/*.parquet"
    output_dir = "data/processed"
    
    try:
        # 1. Buscar todos los archivos Parquet en la carpeta raw
        archivos = glob.glob(path_raw)
        
        if not archivos:
            print("❌ No hay archivos en 'data/raw' para procesar.")
            return

        print(f"📖 Leyendo {len(archivos)} archivos de la carpeta raw...")
        
        # 2. Cargar y combinar todos los archivos en un solo DataFrame
        lista_df = [pd.read_parquet(f) for f in archivos]
        df_unido = pd.concat(lista_df, ignore_index=True)
        
        # 3. TRANSFORMACIONES (Limpieza y Calidad)
        # Eliminamos duplicados por moneda y timestamp para no tener datos repetidos
        df_clean = df_unido.drop_duplicates(subset=['coin_id', 'fetch_timestamp'])
        
        # Añadimos una columna de auditoría para saber cuándo se procesó el dato
        df_clean['processed_at'] = datetime.now().isoformat()
        
        # 4. ALMACENAMIENTO (Processed Layer)
        os.makedirs(output_dir, exist_ok=True)
        ruta_final = os.path.join(output_dir, "crypto_prices_clean.parquet")
        
        # Guardamos el dataset final limpio
        df_clean.to_parquet(ruta_final, engine='pyarrow', index=False)
        
        print(f"✅ Procesamiento completado con éxito.")
        print(f"💾 Dataset limpio guardado en: {ruta_final}")
        print("-" * 30)
        print(df_clean.head())
        print("-" * 30)
        
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")

if __name__ == "__main__":
    procesar_datos()
