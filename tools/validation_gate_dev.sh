#!/usr/bin/env bash
# Validation gate sviluppo (M7 / baby step 9.14):
# Installa la wheel velora-ui in un container Python pulito (NIENTE codice
# velora-ui in editable, NIENTE settings del progetto host) e verifica che
# almeno 5 componenti pubblici renderizzino in un template Django.
#
# Uso:
#   bash tools/validation_gate_dev.sh
#
# Rationale: serve a sgamare regressioni di packaging che la suite di test
# unitaria del repo non vede (es. template/static non inclusi nella wheel,
# app config rotta, import path errato).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WHEEL_PATH=$(ls "${REPO_ROOT}/dist/"velora_ui-*.whl 2>/dev/null | head -n 1 || true)

if [ -z "${WHEEL_PATH}" ]; then
    echo "[validation-gate-dev] dist/velora_ui-*.whl non trovato. Eseguire prima:" >&2
    echo "    docker compose -f docker-compose.dev.yml exec -T web python -m build" >&2
    exit 1
fi

WHEEL_NAME=$(basename "${WHEEL_PATH}")
echo "[validation-gate-dev] uso ${WHEEL_NAME}"

docker run --rm \
    -v "${REPO_ROOT}/dist:/wheels:ro" \
    -v "${REPO_ROOT}/tools/_validation_gate_dev.py:/run_gate.py:ro" \
    python:3.11-slim \
    bash -lc "pip install --quiet '/wheels/${WHEEL_NAME}' 'django>=5,<6' 'django-environ>=0.11' && python /run_gate.py"
