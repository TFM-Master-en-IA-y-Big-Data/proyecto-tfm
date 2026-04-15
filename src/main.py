# src/pipeline_maestro.py
"""
PIPELINE MAESTRO - Version Windows Compatible
"""
import subprocess
import sys
from pathlib import Path
from time import time

sys.path.insert(0, str(Path(__file__).parent))
from logging_config import setup_logging

logger = setup_logging(__name__)

# Lista de etapas del pipeline - AJUSTADAS A TU ESTRUCTURA
ETAPAS = [
    ("[1] Ingesta", "src/pipeline/ingest.py"),
    ("[2] Transformacion", "src/pipeline/transform.py"),
    ("[2.5] Validacion", "src/pipeline/validate.py"),
    ("[3] Features", "src/pipeline/build_dataset.py"),
    ("[4] Entrenamiento", "src/models/train.py"),
    ("[4.5] Evaluacion", "src/models/evaluate.py"),
]

def ejecutar_etapa(nombre, script):
    """Ejecuta una etapa individual"""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f">> {nombre}")
    logger.info("=" * 60)
    
    try:
        inicio = time()
        resultado = subprocess.run(
            [sys.executable, script],
            check=True,
            capture_output=False
        )
        duracion = time() - inicio
        logger.info(f"[OK] {nombre} completada en {duracion:.2f}s")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"[FAIL] {nombre} FALLO")
        logger.error(f"Error: {e}")
        return False

def ejecutar_pipeline_completo():
    """Ejecuta el pipeline completo"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("INICIANDO PIPELINE MAESTRO")
    logger.info("=" * 60)
    
    inicio_total = time()
    etapas_completadas = 0
    
    for nombre, script in ETAPAS:
        if ejecutar_etapa(nombre, script):
            etapas_completadas += 1
        else:
            logger.error("")
            logger.error(f"[PARADO] Pipeline detenido en {nombre}")
            logger.error("Revisa el error arriba")
            break
    
    duracion_total = time() - inicio_total
    
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Etapas completadas: {etapas_completadas}/{len(ETAPAS)}")
    logger.info(f"Tiempo total: {duracion_total:.2f}s")
    
    if etapas_completadas == len(ETAPAS):
        logger.info("[EXITO] Pipeline completado exitosamente!")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    ejecutar_pipeline_completo()