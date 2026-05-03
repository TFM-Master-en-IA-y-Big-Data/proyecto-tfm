from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.models.baseoperator import chain
from datetime import datetime, timedelta
import pendulum
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from models.retrain_calibrated import retrain_calibrated_model
from models.evaluate import evaluar_modelo

default_args = {
    "owner": "Cristian",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
    "email_on_failure": False,
}

with DAG(
    dag_id="weekly_model_training",
    default_args=default_args,
    schedule_interval="0 3 * * 1",   # 3:00 AM hora española cada lunes
    start_date=datetime(2025, 1, 1, tzinfo=pendulum.timezone("Europe/Madrid")),
    catchup=False,
    tags=["crypto", "training"],
) as dag:

    # Espera a que el DAG diario de ese mismo lunes haya terminado
    wait_for_ingestion = ExternalTaskSensor(
        task_id="wait_for_daily_ingestion",
        external_dag_id="daily_crypto_ingestion",
        external_task_id="build_dataset",
        allowed_states=["success"],
        timeout=3600,        # máximo 1h de espera
        poke_interval=120,   # comprueba cada 2 min
        mode="poke",
    )

    task_retrain = PythonOperator(
        task_id="retrain_calibrated",
        python_callable=retrain_calibrated_model,
        # usa DATASET_FEATURES_FILE de config_pipeline directamente,
        # igual que train.py — no necesita args extra
    )

    task_evaluate = PythonOperator(
        task_id="evaluate",
        python_callable=evaluar_modelo,
        # carga MODEL_PATH y DATASET_FEATURES_FILE de config_pipeline
    )

    chain(wait_for_ingestion, task_retrain, task_evaluate)