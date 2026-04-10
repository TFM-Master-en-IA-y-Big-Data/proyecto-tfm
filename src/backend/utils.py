import joblib
import pandas as pd
import os


MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/crypto_model.pkl")
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/storage/")

def cargar_modelo():
    """Carga el modelo entrenado por Cristian"""
    try:
        if os.path.exists(MODEL_PATH):
            return joblib.load(MODEL_PATH)
        return None
    except Exception as e:
        print(f"Error cargando modelo: {e}")
        return None

def obtener_datos_historicos(symbol: str):
    """Simula la lectura de archivos Parquet de Claudia"""
    # En la Fase 3, aquí leeremos los .parquet reales
    pass