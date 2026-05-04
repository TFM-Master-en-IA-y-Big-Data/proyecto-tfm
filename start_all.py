import subprocess
import sys
import time
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
LOG_DIR = PROJECT_ROOT / "logs" / "runtime"
PID_DIR = PROJECT_ROOT / ".pids"

LOG_DIR.mkdir(parents=True, exist_ok=True)
PID_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("runtime")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_DIR / "start_all.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

processes = {}


def pid_file(name):
    return PID_DIR / f"{name}.pid"


def is_running(name):
    file = pid_file(name)

    if not file.exists():
        return False

    try:
        pid = int(file.read_text().strip())
    except Exception:
        file.unlink(missing_ok=True)
        return False

    try:
        if sys.platform == "win32":
            import ctypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION,
                False,
                pid
            )
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                return True
            return False
        else:
            import os
            os.kill(pid, 0)
            return True

    except Exception:
        file.unlink(missing_ok=True)
        return False


def start_process(name, script):
    if is_running(name):
        logger.warning(
            f"{name} ya está en ejecución "
            f"(PID {pid_file(name).read_text().strip()})"
        )
        return

    logger.info(f"Lanzando {name}")

    process = subprocess.Popen(
        [sys.executable, str(PROJECT_ROOT / script)],
        cwd=PROJECT_ROOT
    )

    pid_file(name).write_text(str(process.pid))
    processes[name] = process

    logger.info(f"{name} iniciado (PID {process.pid})")


def stop_all():
    logger.info("Cerrando procesos...")

    for name, process in processes.items():
        if process.poll() is None:
            process.terminate()
            logger.info(f"{name} detenido")

        pid_file(name).unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        start_process("app", "setup.py")
        start_process("scheduler", "scheduler.py")

        logger.info("Sistema iniciado")
        logger.info("Pulsa Ctrl+C para detener")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        stop_all()