# src/ml/train.py
"""
Etapa 4: Entrenamiento del modelo
"""
import pandas as pd
import numpy as np
import joblib
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_pipeline import FEATURES, TARGET, MODEL_PATH, DATASET_FEATURES_FILE, ID_COLS
from logging_config import setup_logging

logger = setup_logging(__name__)


def train_model():
    """Entrena el modelo XGBRegressor sobre el dataset de features."""
    logger.info("[TRAIN] Iniciando entrenamiento...")

    try:
        # ------------------------------------------------------------------
        # 1. Carga del dataset de features (Parquet)
        # ------------------------------------------------------------------
        df = pd.read_parquet(DATASET_FEATURES_FILE)

        logger.info(f"[TRAIN] Cargados {len(df)} registros")
        logger.info(f"[TRAIN] Columnas disponibles: {list(df.columns)}")

        if len(df) == 0:
            raise ValueError("[TRAIN] Dataset vacío, no hay datos para entrenar")

        # ------------------------------------------------------------------
        # 2. Ordenar por crypto y timestamp (crítico para TimeSeriesSplit)
        # ------------------------------------------------------------------
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values(["timestamp", "crypto"]).reset_index(drop=True)

        # ------------------------------------------------------------------
        # 3. Verificar features disponibles
        # ------------------------------------------------------------------
        features_disponibles = [f for f in FEATURES if f in df.columns]
        features_faltantes   = [f for f in FEATURES if f not in df.columns]

        if features_faltantes:
            logger.warning(f"[TRAIN] Features no encontradas en el dataset: {features_faltantes}")

        logger.info(f"[TRAIN] Features que entran al modelo: {features_disponibles}")

        # ------------------------------------------------------------------
        # 4. Verificar target
        # ------------------------------------------------------------------
        if TARGET not in df.columns:
            raise ValueError(f"[TRAIN] Columna target '{TARGET}' no encontrada en el dataset")

        # ------------------------------------------------------------------
        # 5. Eliminar filas con NaN en features o target (warm-up de ventanas)
        # ------------------------------------------------------------------
        df_model = df.dropna(subset=features_disponibles + [TARGET])
        logger.info(f"[TRAIN] Filas tras eliminar NaN de warm-up: {len(df_model)} "
                    f"({len(df) - len(df_model)} eliminadas)")

        X = df_model[features_disponibles]
        y = df_model[TARGET]

        logger.info(f"[TRAIN] X shape: {X.shape} | y shape: {y.shape}")
        logger.info(f"[TRAIN] Target — min: {y.min():.4f} | max: {y.max():.4f} | mean: {y.mean():.4f}")

        # ------------------------------------------------------------------
        # 6. Validación cruzada temporal (TimeSeriesSplit)
        # ------------------------------------------------------------------
        n_splits = 5
        tscv     = TimeSeriesSplit(n_splits=n_splits)
        scores   = []

        logger.info(f"[TRAIN] Ejecutando validación cruzada temporal con {n_splits} folds...")

        for i, (train_idx, test_idx) in enumerate(tscv.split(X)):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            logger.info(f"[TRAIN] Fold {i+1}: train={len(train_idx)} filas | test={len(test_idx)} filas")

            fold_model = XGBRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbosity=0,
            )
            fold_model.fit(X_train, y_train)

            y_pred = fold_model.predict(X_test)

            mae  = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2   = r2_score(y_test, y_pred)

            scores.append({"mae": mae, "rmse": rmse, "r2": r2})
            logger.info(f"[TRAIN] Fold {i+1}: MAE={mae:.4f} | RMSE={rmse:.4f} | R²={r2:.4f}")

        # Resumen de métricas
        scores_df = pd.DataFrame(scores)
        logger.info(f"[TRAIN] Métricas medias — "
                    f"MAE={scores_df['mae'].mean():.4f} | "
                    f"RMSE={scores_df['rmse'].mean():.4f} | "
                    f"R²={scores_df['r2'].mean():.4f}")

        # ------------------------------------------------------------------
        # 7. Entrenamiento final sobre todos los datos
        # ------------------------------------------------------------------
        logger.info("[TRAIN] Entrenando modelo final sobre todos los datos...")

        model = XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbosity=0,
        )
        model.fit(X, y)

        # ------------------------------------------------------------------
        # 8. Importancia de features
        # ------------------------------------------------------------------
        feature_importance = pd.Series(
            model.feature_importances_,
            index=features_disponibles
        ).sort_values(ascending=False)

        logger.info(f"[TRAIN] Importancia de features:\n{feature_importance.to_string()}")

        # ------------------------------------------------------------------
        # 9. Guardar modelo
        # ------------------------------------------------------------------
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, MODEL_PATH)

        logger.info(f"[TRAIN] Modelo guardado en: {MODEL_PATH}")
        logger.info("[TRAIN] ✅ Entrenamiento completado")

        return model

    except Exception as e:
        logger.error(f"[TRAIN] Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    train_model()