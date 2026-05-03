#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

SKIP_PIPELINE=0
for arg in "$@"; do
  case "$arg" in
    --skip-pipeline) SKIP_PIPELINE=1 ;;
    *) echo "Uso: bash start_all.sh [--skip-pipeline]"; exit 1 ;;
  esac
done

if [ "$SKIP_PIPELINE" -eq 0 ]; then
  python src/main.py
fi

python -m uvicorn src.backend.main:app --reload --host 127.0.0.1 --port 8000 &
API_PID=$!

(cd src/frontend && python -m http.server 8080) &
FRONT_PID=$!

cleanup() {
  kill "$API_PID" "$FRONT_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "API:      http://127.0.0.1:8000"
echo "Frontend: http://localhost:8080"

wait
