# src/ml/retrain_calibrated.py
"""
Reentrenamiento del modelo con mejor calibración
"""
import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from sklearn.model_selection import TimeSeriesSplit
from sklearn.calibration import CalibratedClassifierCV
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_pipeline import FEATURES, TARGET, MODEL_PATH, DATASET_FEATURES_FILE
from logging_config import setup_logging

logger = setup_logging(__name__)

def retrain_calibrated_model():
    """Reentena el modelo con calibración para mejores predicciones"""
    logger.info("[RETRAIN] Iniciando reentrenamiento calibrado...")
    
    try:
        # Cargar datos
        df = pd.read_csv(DATASET_FEATURES_FILE)
        
        logger.info(f"[RETRAIN] Datos cargados: {len(df)} registros")
        logger.info(f"[RETRAIN] Distribución targets: {df[TARGET].value_counts().to_dict()}")
        
        X = df[FEATURES]
        y = df[TARGET]
        
        # Validación temporal
        tscv = TimeSeriesSplit(n_splits=5)
        
        logger.info("[RETRAIN] Entrenando con calibración...")
        
        # Modelo base
        base_model = XGBClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric="logloss",
            verbosity=0,
            scale_pos_weight=1.0  # ✅ Balancear clases
        )
        
        # Modelo calibrado
        model = CalibratedClassifierCV(base_model, method='sigmoid', cv=5)
        
        # Entrenar
        model.fit(X, y)
        
        # Evaluar
        y_pred = model.predict(X)
        y_pred_proba = model.predict_proba(X)[:, 1]
        
        accuracy = accuracy_score(y, y_pred)
        roc_auc = roc_auc_score(y, y_pred_proba)
        
        logger.info(f"[RETRAIN] Accuracy: {accuracy:.4f}")
        logger.info(f"[RETRAIN] ROC-AUC: {roc_auc:.4f}")
        logger.info(f"[RETRAIN] Classification Report:\n{classification_report(y, y_pred)}")
        
        # Contar predicciones
        subidas = (y_pred == 1).sum()
        bajadas = (y_pred == 0).sum()
        logger.info(f"[RETRAIN] Predicciones - Subidas: {subidas}, Bajadas: {bajadas}")
        
        # Guardar
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, str(MODEL_PATH))
        
        logger.info(f"[RETRAIN] Modelo guardado en: {MODEL_PATH}")
        logger.info("[RETRAIN] ✅ Reentrenamiento completado")
        
        return model
        
    except Exception as e:
        logger.error(f"[RETRAIN] Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    retrain_calibrated_model()