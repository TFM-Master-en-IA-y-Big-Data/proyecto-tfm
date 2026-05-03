# src/ml/retrain_calibrated.py
"""
Reentrenamiento del modelo con calibración de predicciones
"""
import pandas as pd
import numpy as np
import joblib
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_pipeline import FEATURES, TARGET, MODEL_PATH, DATASET_FEATURES_FILE
from logging_config import setup_logging

logger = setup_logging(__name__)


def retrain_calibrated_model():
    """
    Reentrenamiento con hiperparámetros refinados respecto a train.py:
    - Mayor número de estimadores (150 vs 100)
    - Learning rate más bajo (0.05 vs 0.1) para mejor generalización
    - Menor profundidad (4 vs 5) para reducir overfitting
    - early_stopping_rounds para detener cuando no mejora
    """
    logger.info("[RETRAIN] Iniciando reentrenamiento calibrado...")

    try:
        # ------------------------------------------------------------------
        # 1. Carga del dataset de features (Parquet)
        # ------------------------------------------------------------------
        df = pd.read_parquet(DATASET_FEATURES_FILE)

        logger.info(f"[RETRAIN] Cargados {len(df)} registros")
        logger.info(f"[RETRAIN] Columnas disponibles: {list(df.columns)}")

        if len(df) == 0:
            raise ValueError("[RETRAIN] Dataset vacío")

        # ------------------------------------------------------------------
        # 2. Ordenar por crypto y timestamp
        # ------------------------------------------------------------------
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values(["timestamp", "crypto"]).reset_index(drop=True)

        # ------------------------------------------------------------------
        # 3. Verificar features y target
        # ------------------------------------------------------------------
        features_disponibles = [f for f in FEATURES if f in df.columns]
        features_faltantes   = [f for f in FEATURES if f not in df.columns]

        if features_faltantes:
            logger.warning(f"[RETRAIN] Features no encontradas: {features_faltantes}")

        if TARGET not in df.columns:
            raise ValueError(f"[RETRAIN] Columna target '{TARGET}' no encontrada")

        # ------------------------------------------------------------------
        # 4. Eliminar NaN de warm-up de ventanas temporales
        # ------------------------------------------------------------------
        df_model = df.dropna(subset=features_disponibles + [TARGET])
        logger.info(f"[RETRAIN] Filas tras eliminar NaN: {len(df_model)} "
                    f"({len(df) - len(df_model)} eliminadas)")

        X = df_model[features_disponibles]
        y = df_model[TARGET]

        logger.info(f"[RETRAIN] X shape: {X.shape} | y shape: {y.shape}")
        logger.info(f"[RETRAIN] Target — min: {y.min():.4f} | max: {y.max():.4f} | mean: {y.mean():.4f}")

        # ------------------------------------------------------------------
        # 5. Validación cruzada temporal con early stopping
        # ------------------------------------------------------------------
        n_splits = 5
        tscv     = TimeSeriesSplit(n_splits=n_splits)
        scores   = []

        logger.info(f"[RETRAIN] Validación cruzada temporal con {n_splits} folds...")

        for i, (train_idx, test_idx) in enumerate(tscv.split(X)):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            logger.info(f"[RETRAIN] Fold {i+1}: train={len(train_idx)} | test={len(test_idx)}")

            fold_model = XGBRegressor(
                n_estimators=500,          # alto para que early stopping decida
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbosity=0,
                early_stopping_rounds=20,
            )
            fold_model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                verbose=False,
            )

            y_pred = fold_model.predict(X_test)

            mae  = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2   = r2_score(y_test, y_pred)

            scores.append({"mae": mae, "rmse": rmse, "r2": r2,
                           "best_iteration": fold_model.best_iteration})
            logger.info(f"[RETRAIN] Fold {i+1}: MAE={mae:.4f} | RMSE={rmse:.4f} | "
                        f"R²={r2:.4f} | best_iter={fold_model.best_iteration}")

        scores_df = pd.DataFrame(scores)
        best_n_estimators = int(scores_df["best_iteration"].mean())

        logger.info(f"[RETRAIN] Métricas medias — "
                    f"MAE={scores_df['mae'].mean():.4f} | "
                    f"RMSE={scores_df['rmse'].mean():.4f} | "
                    f"R²={scores_df['r2'].mean():.4f}")
        logger.info(f"[RETRAIN] Número óptimo de estimadores (media folds): {best_n_estimators}")

        # ------------------------------------------------------------------
        # 6. Entrenamiento final con n_estimators óptimo
        # ------------------------------------------------------------------
        logger.info(f"[RETRAIN] Entrenando modelo final con {best_n_estimators} estimadores...")

        model = XGBRegressor(
            n_estimators=best_n_estimators,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbosity=0,
        )
        model.fit(X, y)

        # ------------------------------------------------------------------
        # 7. Métricas finales sobre todo el conjunto
        # ------------------------------------------------------------------
        y_pred_final = model.predict(X)
        mae_final  = mean_absolute_error(y, y_pred_final)
        rmse_final = np.sqrt(mean_squared_error(y, y_pred_final))
        r2_final   = r2_score(y, y_pred_final)

        logger.info(f"[RETRAIN] Métricas finales (train completo) — "
                    f"MAE={mae_final:.4f} | RMSE={rmse_final:.4f} | R²={r2_final:.4f}")

        # ------------------------------------------------------------------
        # 8. Importancia de features
        # ------------------------------------------------------------------
        feature_importance = pd.Series(
            model.feature_importances_,
            index=features_disponibles
        ).sort_values(ascending=False)

        logger.info(f"[RETRAIN] Importancia de features:\n{feature_importance.to_string()}")

        # ------------------------------------------------------------------
        # 9. Guardar modelo
        # ------------------------------------------------------------------
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        fecha = datetime.now().strftime("%Y-%m-%d")
        model_path_versioned = MODEL_PATH.parent / f"model_{fecha}.pkl"
        joblib.dump(model, model_path_versioned)
        joblib.dump(model, MODEL_PATH)

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