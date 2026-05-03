import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def _terminate_process(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-pipeline", action="store_true")
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent

    if not args.skip_pipeline:
        pipeline = subprocess.run([sys.executable, "src/main.py"], cwd=root_dir)
        if pipeline.returncode != 0:
            return pipeline.returncode

    env = os.environ.copy()

    api_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.backend.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd=root_dir,
        env=env,
    )
    frontend_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8080"],
        cwd=root_dir / "src" / "frontend",
        env=env,
    )

    print("API:      http://127.0.0.1:8000")
    print("Frontend: http://localhost:8080")

    try:
        while True:
            if api_proc.poll() is not None:
                return api_proc.returncode or 0
            if frontend_proc.poll() is not None:
                return frontend_proc.returncode or 0
            time.sleep(0.5)
    except KeyboardInterrupt:
        return 0
    finally:
        _terminate_process(frontend_proc)
        _terminate_process(api_proc)


if __name__ == "__main__":
    raise SystemExit(main())
