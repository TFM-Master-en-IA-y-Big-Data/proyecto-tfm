# src/main.py
"""
PIPELINE MAESTRO
"""
import os
import subprocess
import sys
from pathlib import Path
from time import time

sys.path.insert(0, str(Path(__file__).parent))
from logging_config import setup_logging

logger = setup_logging(__name__)

# Necesario para Spark
os.environ["JAVA_HOME"]      = "C:/Program Files/Java/jdk-21"
os.environ["PYSPARK_PYTHON"] = "python"

# Rutas absolutas basadas en la ubicacion de este fichero
BASE_DIR = Path(__file__).parent.parent  # sube de src/ a la raiz del proyecto

ETAPAS = [
    ("[1]   Ingesta",         BASE_DIR / "src/pipeline/ingest.py"),
    ("[2]   Transformacion",  BASE_DIR / "src/pipeline/transform.py"),
    ("[2.5] Validacion",      BASE_DIR / "src/pipeline/validate.py"),
    ("[3]   Features",        BASE_DIR / "src/pipeline/build_dataset.py"),
    ("[4]   Entrenamiento",   BASE_DIR / "src/models/train.py"),
    ("[4.1] Reentrenamiento", BASE_DIR / "src/models/retrain_calibrated.py"),
    ("[4.5] Evaluacion",      BASE_DIR / "src/models/evaluate.py"),
]

def ejecutar_etapa(nombre: str, script: Path) -> bool:
    """Ejecuta una etapa individual del pipeline."""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f">> {nombre}")
    logger.info("=" * 60)

    if not script.exists():
        logger.error(f"[FAIL] Script no encontrado: {script}")
        return False

    try:
        inicio = time()
        subprocess.run(
            [sys.executable, str(script)],
            check=True,
            capture_output=False,
        )
        duracion = time() - inicio
        logger.info(f"[OK] {nombre} completada en {duracion:.2f}s")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"[FAIL] {nombre} FALLO - codigo de salida: {e.returncode}")
        return False


def ejecutar_pipeline_completo():
    """Ejecuta el pipeline completo etapa a etapa."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("INICIANDO PIPELINE MAESTRO")
    logger.info("=" * 60)

    inicio_total       = time()
    etapas_completadas = 0

    for nombre, script in ETAPAS:
        if ejecutar_etapa(nombre, script):
            etapas_completadas += 1
        else:
            logger.error("")
            logger.error(f"[PARADO] Pipeline detenido en: {nombre}")
            logger.error("Revisa el error arriba antes de continuar")
            break

    duracion_total = time() - inicio_total

    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Etapas completadas : {etapas_completadas}/{len(ETAPAS)}")
    logger.info(f"Tiempo total       : {duracion_total:.2f}s")

    if etapas_completadas == len(ETAPAS):
        logger.info("[EXITO] Pipeline completado correctamente")
    else:
        logger.warning("[INCOMPLETO] El pipeline no finalizo todas las etapas")

    logger.info("=" * 60)


if __name__ == "__main__":
    ejecutar_pipeline_completo()