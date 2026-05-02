# src/ml/evaluate.py
"""
Etapa 4.5: Evaluación del modelo entrenado

Incluye:
- Métricas globales in-sample
- Holdout temporal real (último 20%)
- Validación temporal por folds reentrenando en cada fold
- Métricas por crypto
- Exportación de predicciones
"""

import pandas as pd
import numpy as np
import joblib

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBRegressor

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config_pipeline import (
    FEATURES,
    TARGET,
    MODEL_PATH,
    DATASET_FEATURES_FILE,
    OUTPUTS_DIR,
)

from logging_config import setup_logging

logger = setup_logging(__name__)


def _build_model_from_loaded(model):
    """
    Construye un nuevo XGBRegressor reutilizando
    hiperparámetros del modelo cargado.
    """
    return XGBRegressor(
        n_estimators=model.n_estimators,
        max_depth=model.max_depth,
        learning_rate=model.learning_rate,
        subsample=model.subsample,
        colsample_bytree=model.colsample_bytree,
        random_state=42,
        verbosity=0,
    )


def evaluar_modelo():
    logger.info("[EVALUATE] Iniciando evaluación del modelo...")

    try:
        # --------------------------------------------------------------
        # 1. Cargar modelo
        # --------------------------------------------------------------
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"[EVALUATE] Modelo no encontrado en: {MODEL_PATH}"
            )

        model = joblib.load(MODEL_PATH)

        logger.info(f"[EVALUATE] Modelo cargado desde: {MODEL_PATH}")

        # --------------------------------------------------------------
        # 2. Cargar dataset
        # --------------------------------------------------------------
        df = pd.read_parquet(DATASET_FEATURES_FILE)

        if len(df) == 0:
            raise ValueError("[EVALUATE] Dataset vacío")

        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Orden temporal global
        df = df.sort_values(["timestamp", "crypto"]).reset_index(drop=True)

        logger.info(f"[EVALUATE] Dataset cargado: {len(df)} filas")

        # --------------------------------------------------------------
        # 3. Preparación
        # --------------------------------------------------------------
        features_disponibles = [f for f in FEATURES if f in df.columns]
        features_faltantes = [f for f in FEATURES if f not in df.columns]

        if features_faltantes:
            logger.warning(
                f"[EVALUATE] Features no encontradas: {features_faltantes}"
            )

        if TARGET not in df.columns:
            raise ValueError(
                f"[EVALUATE] Columna target '{TARGET}' no encontrada"
            )

        df_model = df.dropna(subset=features_disponibles + [TARGET])

        logger.info(
            f"[EVALUATE] Filas tras eliminar NaN: {len(df_model)} "
            f"({len(df) - len(df_model)} eliminadas)"
        )

        X = df_model[features_disponibles]
        y = df_model[TARGET]

        # --------------------------------------------------------------
        # 4. Evaluación global in-sample
        # --------------------------------------------------------------
        y_pred = model.predict(X)

        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        r2 = r2_score(y, y_pred)

        logger.info("=" * 60)
        logger.info("[EVALUATE] MÉTRICAS GLOBALES (IN-SAMPLE)")
        logger.info("=" * 60)
        logger.info(f"MAE  : {mae:.4f}")
        logger.info(f"RMSE : {rmse:.4f}")
        logger.info(f"R²   : {r2:.4f}")

        # --------------------------------------------------------------
        # 5. Holdout temporal real (último 20%)
        # --------------------------------------------------------------
        logger.info("=" * 60)
        logger.info("[EVALUATE] HOLDOUT TEMPORAL (OUT-OF-SAMPLE)")
        logger.info("=" * 60)

        split_idx = int(len(X) * 0.8)

        X_train_holdout = X.iloc[:split_idx]
        y_train_holdout = y.iloc[:split_idx]

        X_test_holdout = X.iloc[split_idx:]
        y_test_holdout = y.iloc[split_idx:]

        holdout_model = _build_model_from_loaded(model)

        holdout_model.fit(X_train_holdout, y_train_holdout)

        y_pred_holdout = holdout_model.predict(X_test_holdout)

        mae_h = mean_absolute_error(y_test_holdout, y_pred_holdout)
        rmse_h = np.sqrt(mean_squared_error(y_test_holdout, y_pred_holdout))
        r2_h = r2_score(y_test_holdout, y_pred_holdout)

        logger.info(f"Train: {len(X_train_holdout)} filas")
        logger.info(f"Test : {len(X_test_holdout)} filas")
        logger.info(f"MAE  : {mae_h:.4f}")
        logger.info(f"RMSE : {rmse_h:.4f}")
        logger.info(f"R²   : {r2_h:.4f}")

        # --------------------------------------------------------------
        # 6. Validación temporal por folds
        # --------------------------------------------------------------
        logger.info("=" * 60)
        logger.info("[EVALUATE] VALIDACIÓN TEMPORAL POR FOLDS")
        logger.info("=" * 60)

        tscv = TimeSeriesSplit(n_splits=5)
        scores = []

        for i, (train_idx, test_idx) in enumerate(tscv.split(X)):
            X_train = X.iloc[train_idx]
            X_test = X.iloc[test_idx]

            y_train = y.iloc[train_idx]
            y_test = y.iloc[test_idx]

            fold_model = _build_model_from_loaded(model)

            fold_model.fit(X_train, y_train)

            y_pred_fold = fold_model.predict(X_test)

            mae_f = mean_absolute_error(y_test, y_pred_fold)
            rmse_f = np.sqrt(mean_squared_error(y_test, y_pred_fold))
            r2_f = r2_score(y_test, y_pred_fold)

            scores.append(
                {
                    "fold": i + 1,
                    "mae": mae_f,
                    "rmse": rmse_f,
                    "r2": r2_f,
                }
            )

            logger.info(
                f"Fold {i+1}: "
                f"MAE={mae_f:.4f} | "
                f"RMSE={rmse_f:.4f} | "
                f"R²={r2_f:.4f}"
            )

        scores_df = pd.DataFrame(scores)

        logger.info(
            f"Media folds: "
            f"MAE={scores_df['mae'].mean():.4f} | "
            f"RMSE={scores_df['rmse'].mean():.4f} | "
            f"R²={scores_df['r2'].mean():.4f}"
        )

        # --------------------------------------------------------------
        # 7. Métricas por crypto
        # --------------------------------------------------------------
        logger.info("=" * 60)
        logger.info("[EVALUATE] MÉTRICAS POR CRYPTO")
        logger.info("=" * 60)

        df_eval = df_model.copy()
        df_eval["y_pred"] = y_pred
        df_eval["error"] = (df_eval[TARGET] - df_eval["y_pred"]).abs()

        for crypto in sorted(df_eval["crypto"].unique()):
            df_crypto = df_eval[df_eval["crypto"] == crypto]

            y_true_c = df_crypto[TARGET].values
            y_pred_c = df_crypto["y_pred"].values

            mae_c = mean_absolute_error(y_true_c, y_pred_c)
            rmse_c = np.sqrt(mean_squared_error(y_true_c, y_pred_c))
            r2_c = r2_score(y_true_c, y_pred_c)

            logger.info(
                f"{crypto:<15} "
                f"MAE={mae_c:.4f} | "
                f"RMSE={rmse_c:.4f} | "
                f"R²={r2_c:.4f}"
            )

        # --------------------------------------------------------------
        # 8. Importancia de features
        # --------------------------------------------------------------
        if hasattr(model, "feature_importances_"):
            feature_importance = pd.Series(
                model.feature_importances_,
                index=features_disponibles,
            ).sort_values(ascending=False)

            logger.info("=" * 60)
            logger.info("[EVALUATE] IMPORTANCIA DE FEATURES")
            logger.info("=" * 60)
            logger.info(f"\n{feature_importance.to_string()}")

        # --------------------------------------------------------------
        # 9. Exportar predicciones
        # --------------------------------------------------------------
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

        output_file = OUTPUTS_DIR / "predicciones_evaluacion.csv"

        df_out = df_eval[
            ["crypto", "timestamp", TARGET, "y_pred", "error"]
        ].copy()

        df_out = df_out.rename(
            columns={
                TARGET: "y_real",
                "y_pred": "y_predicho",
            }
        )

        df_out.to_csv(output_file, index=False)

        logger.info("=" * 60)
        logger.info(f"[EVALUATE] Predicciones exportadas: {output_file}")
        logger.info("[EVALUATE] ✅ Evaluación completada")

        return scores_df

    except Exception as e:
        logger.error(f"[EVALUATE] Error: {e}")

        import traceback
        logger.error(traceback.format_exc())

        raise


if __name__ == "__main__":
    evaluar_modelo()