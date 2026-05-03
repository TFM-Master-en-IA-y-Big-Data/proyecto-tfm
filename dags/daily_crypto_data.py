from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.models.baseoperator import chain
from datetime import datetime, timedelta
import sys
import pendulum
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from pipeline.ingest import descargar_datos
from pipeline.transform import procesar_datos
from pipeline.validate import validar_dataset
from pipeline.build_dataset import build_dataset

default_args = {
    "owner": "Cristian",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

with DAG(
    dag_id="daily_crypto_ingestion",
    default_args=default_args,
    schedule_interval="0 1 * * *",   # 1:00 AM hora española
    start_date=datetime(2025, 1, 1, tzinfo=pendulum.timezone("Europe/Madrid")),
    catchup=False,
    tags=["crypto", "ingestion"],
) as dag:

    task_ingest = PythonOperator(
        task_id="ingest",
        python_callable=descargar_datos,
        # descargar_datos() no recibe args: usa datetime.now() internamente
    )

    task_transform = PythonOperator(
        task_id="transform",
        python_callable=procesar_datos,
    )

    # ShortCircuitOperator: si validar_dataset() devuelve False,
    # cancela el resto del DAG sin marcarlo como fallido
    task_validate = ShortCircuitOperator(
        task_id="validate",
        python_callable=validar_dataset,
    )

    task_build = PythonOperator(
        task_id="build_dataset",
        python_callable=build_dataset,
    )

    chain(task_ingest, task_transform, task_validate, task_build)