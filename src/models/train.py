# src/ml/train.py
"""
Etapa 4: Entrenamiento del modelo
"""
import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from sklearn.model_selection import TimeSeriesSplit
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_pipeline import FEATURES, TARGET, MODEL_PATH, DATASET_FEATURES_FILE
from logging_config import setup_logging

logger = setup_logging(__name__)

def train_model():
    """Entrena el modelo XGBoost"""
    logger.info("[TRAIN] Iniciando entrenamiento...")
    
    try:
        # Lee features ya generados
        df = pd.read_csv(DATASET_FEATURES_FILE)
        
        logger.info(f"[TRAIN] Cargados {len(df)} registros")
        logger.info(f"[TRAIN] Columnas disponibles: {list(df.columns)}")
        
        if len(df) == 0:
            logger.error("[TRAIN] Dataset vacio, no hay datos para entrenar")
            raise ValueError("Dataset vacio")
        
        # Verificar que existan las columnas necesarias
        features_disponibles = [f for f in FEATURES if f in df.columns]
        logger.info(f"[TRAIN] Features disponibles: {features_disponibles}")
        
        if not features_disponibles:
            logger.warning("[TRAIN] No hay features disponibles, usando solo features basicos")
            features_disponibles = [col for col in df.columns if col not in ['coin', 'timestamp', 'target']]
        
        # Si no tenemos target, crear dummy
        if TARGET not in df.columns:
            logger.warning(f"[TRAIN] Columna '{TARGET}' no encontrada, creando target dummy")
            df[TARGET] = 0
        
        X = df[features_disponibles]
        y = df[TARGET]
        
        logger.info(f"[TRAIN] X shape: {X.shape}, y shape: {y.shape}")
        
        # Validacion temporal
        tscv = TimeSeriesSplit(n_splits=min(5, len(df) // 2))
        scores = []

        logger.info(f"[TRAIN] Ejecutando validacion cruzada con {tscv.get_n_splits()} folds...")
        
        for i, (train_idx, test_idx) in enumerate(tscv.split(X)):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            logger.info(f"[TRAIN] Fold {i+1}: train_size={len(train_idx)}, test_size={len(test_idx)}")
            
            model = XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                eval_metric="logloss",
                verbosity=0
            )

            model.fit(X_train, y_train, verbose=False)

            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1]

            acc = accuracy_score(y_test, y_pred)
            roc = roc_auc_score(y_test, y_prob) if len(y_test.unique()) > 1 else 0.0

            scores.append((acc, roc))
            logger.info(f"[TRAIN] Fold {i+1}: Accuracy={acc:.4f}, ROC-AUC={roc:.4f}")

        # Entrenamiento final
        logger.info("[TRAIN] Entrenando modelo final...")
        model = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric="logloss",
            verbosity=0
        )
        
        model.fit(X, y, verbose=False)

        # Guardar
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, MODEL_PATH)

        logger.info(f"[TRAIN] Modelo guardado en: {MODEL_PATH}")
        logger.info("[TRAIN] Entrenamiento completado")
        
        return model

    except Exception as e:
        logger.error(f"[TRAIN] Error: {e}")
        raise

if __name__ == "__main__":
    train_model()