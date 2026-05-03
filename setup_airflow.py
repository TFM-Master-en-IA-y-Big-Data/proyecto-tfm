import subprocess
import os
from pathlib import Path

env = os.environ.copy()
env["AIRFLOW_HOME"]                        = str(Path.home() / "airflow")
env["AIRFLOW__CORE__DAGS_FOLDER"]          = str(Path(__file__).parent / "dags")
env["AIRFLOW__CORE__LOAD_EXAMPLES"]        = "False"
env["AIRFLOW__WEBSERVER__WEB_SERVER_PORT"] = "8081"

subprocess.run(["airflow", "db", "init"], env=env, check=True)

# Lanza en background y no bloquea
subprocess.Popen(
    ["airflow", "standalone"],
    env=env,
    stdout=open(Path.home() / "airflow/airflow.log", "a"),
    stderr=subprocess.STDOUT,
)