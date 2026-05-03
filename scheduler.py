# scheduler.py
import schedule
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline.ingest import descargar_datos
from pipeline.transform import procesar_datos
from pipeline.validate import validar_dataset
from pipeline.build_dataset import build_dataset
from models.retrain_calibrated import retrain_calibrated_model
from models.evaluate import evaluar_modelo


def pipeline_diario():
    print("[SCHEDULER] Ejecutando pipeline diario...")
    descargar_datos()
    procesar_datos()
    if validar_dataset():
        build_dataset()
    else:
        print("[SCHEDULER] Validación fallida, build_dataset cancelado")


def pipeline_semanal():
    print("[SCHEDULER] Ejecutando pipeline semanal...")
    pipeline_diario()
    retrain_calibrated_model()
    evaluar_modelo()


schedule.every().day.at("01:00").do(pipeline_diario)
schedule.every().monday.at("03:00").do(pipeline_semanal)

print("[SCHEDULER] Scheduler iniciado. Esperando...")
print("[SCHEDULER] Pipeline diario: cada día a la 1:00 AM")
print("[SCHEDULER] Pipeline semanal: cada lunes a las 3:00 AM")

while True:
    schedule.run_pending()
    time.sleep(60)