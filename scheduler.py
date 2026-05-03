import schedule
import time
import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent
LOG_DIR = PROJECT_ROOT / "logs" / "scheduler"
LOG_DIR.mkdir(parents=True, exist_ok=True)

log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"

logger = logging.getLogger("scheduler")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pipeline.ingest import descargar_datos
from pipeline.transform import procesar_datos
from pipeline.validate import validar_dataset
from pipeline.build_dataset import build_dataset
from models.retrain_calibrated import retrain_calibrated_model
from models.evaluate import evaluar_modelo


def run_step(name, fn):
    start = datetime.now()
    logger.info(f"[START] {name}")

    try:
        result = fn()
        elapsed = (datetime.now() - start).total_seconds()
        logger.info(f"[OK] {name} finalizado en {elapsed:.2f}s")
        return result

    except Exception as e:
        elapsed = (datetime.now() - start).total_seconds()
        logger.error(f"[ERROR] {name} falló tras {elapsed:.2f}s")
        logger.error(str(e))
        logger.error(traceback.format_exc())
        raise


def pipeline_diario():
    logger.info("========================================")
    logger.info("INICIO PIPELINE DIARIO")
    logger.info("========================================")

    try:
        run_step("descargar_datos", descargar_datos)
        run_step("procesar_datos", procesar_datos)

        valid = run_step("validar_dataset", validar_dataset)

        if valid:
            run_step("build_dataset", build_dataset)
            logger.info("Pipeline diario completado correctamente")
        else:
            logger.warning(
                "Validación fallida. build_dataset cancelado"
            )

    except Exception:
        logger.error("Pipeline diario abortado por error")


def pipeline_semanal():
    logger.info("========================================")
    logger.info("INICIO PIPELINE SEMANAL")
    logger.info("========================================")

    try:
        pipeline_diario()
        run_step("retrain_calibrated_model", retrain_calibrated_model)
        run_step("evaluar_modelo", evaluar_modelo)

        logger.info("Pipeline semanal completado correctamente")

    except Exception:
        logger.error("Pipeline semanal abortado por error")


schedule.every().day.at("01:00").do(pipeline_diario)
schedule.every().monday.at("03:00").do(pipeline_semanal)

logger.info("Scheduler iniciado")
logger.info("Pipeline diario: cada día a las 01:00")
logger.info("Pipeline semanal: cada lunes a las 03:00")

while True:
    try:
        schedule.run_pending()

    except Exception:
        logger.error("Error en el loop principal del scheduler")
        logger.error(traceback.format_exc())

    time.sleep(60)