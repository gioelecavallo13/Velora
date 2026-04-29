#!/usr/bin/env bash
# Deploy rsync + docker compose su VPS (produzione + overlay Traefik).
# Non esegue mai `docker compose down -v`.
#
# Produzione: ad ogni deploy: `build --no-cache` (compatibile Compose vecchi: --no-cache non sta su `up`),
# poi `up --force-recreate --remove-orphans` così db/nginx/web si allineano.
#
# Uso:
#   cp scripts/deploy.env.example scripts/deploy.env   # una tantum, compila le variabili
#   ./scripts/deploy-vps.sh
#   ./scripts/deploy-vps.sh --dry-run                   # solo rsync a secco + niente compose remoto
#   ./scripts/deploy-vps.sh --upload-env-prod         # dopo rsync copia .env.prod locale → VPS (scp), poi compose
#
# Prerequisiti sulla VPS (path = DEPLOY_PATH):
# - File `.env.prod` NON passa con rsync (escluso): va creato sulla VPS o copiato una tantum, es.:
#     scp .env.prod.example ubuntu@HOST:/opt/velora/.env.prod   # poi edit su server
#   oppure usa `--upload-env-prod` se hai già `.env.prod` in root repo (gitignored).
#   Deve contenere `VELORA_PUBLIC_HOST=<FQDN>` come in DNS/Traefik (+ segreti Django/Postgres).
#

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DEPLOY_ENV="${DEPLOY_ENV:-$ROOT/scripts/deploy.env}"
if [[ ! -f "$DEPLOY_ENV" ]]; then
  echo "Manca $DEPLOY_ENV — copia scripts/deploy.env.example in scripts/deploy.env." >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$DEPLOY_ENV"

# Compatibilità naming con progetti tipo Sondaggi
if [[ -z "${DEPLOY_HOST:-}" ]] && [[ -n "${VPS_HOST:-}" ]]; then
  DEPLOY_HOST="${SSH_USER:-ubuntu}@${VPS_HOST}"
fi

: "${DEPLOY_HOST:?Imposta DEPLOY_HOST (ssh user@host) o VPS_HOST (+ SSH_USER) in scripts/deploy.env}"
DEPLOY_PATH="${DEPLOY_PATH:-${DOCKER_COMPOSE_PATH:-/opt/velora}}"

if [[ "$DEPLOY_PATH" == /data/* ]]; then
  echo "DEPLOY_PATH non deve essere sotto /data/ (solo tree applicativo, es. /opt/velora)." >&2
  exit 1
fi

DRY_RUN=false
UPLOAD_ENV_PROD=false
for arg in "$@"; do
  if [[ "$arg" == "--dry-run" ]]; then
    DRY_RUN=true
  fi
  if [[ "$arg" == "--upload-env-prod" ]]; then
    UPLOAD_ENV_PROD=true
  fi
done

SSH_PORT="${SSH_PORT:-22}"
SSH_OPTS=(-p "$SSH_PORT")
if [[ -n "${SSH_IDENTITY_FILE:-}" ]]; then
  SSH_OPTS+=(-i "$SSH_IDENTITY_FILE")
fi

RSYNC_RSH=$(printf '%q ' ssh "${SSH_OPTS[@]}")
RSYNC_RSH=${RSYNC_RSH%% }

RSYNC_FLAGS=(-az)
if [[ "$DRY_RUN" == true ]]; then
  RSYNC_FLAGS+=(-n --itemize-changes)
fi

RSYNC_EXCLUDES=(
  --exclude='.git/'
  --exclude='node_modules/'
  --exclude='.venv/'
  --exclude='venv/'
  --exclude='__pycache__/'
  --exclude='*.egg-info/'
  --exclude='.pytest_cache/'
  --exclude='.mypy_cache/'
  --exclude='.ruff_cache/'
  --exclude='htmlcov/'
  --exclude='playwright-report/'
  --exclude='test-results/'
  --exclude='.env'
  --exclude='.env.prod'
  --exclude='scripts/deploy.env'
  --exclude='media/'
  --exclude='staticfiles/'
  --exclude='data/db.sqlite3'
  --exclude='db.sqlite3'
  --exclude='*.log'
  --exclude='dist/'
  --exclude='build/'
)

echo "Rsync → ${DEPLOY_HOST}:${DEPLOY_PATH}/"
rsync "${RSYNC_FLAGS[@]}" \
  "${RSYNC_EXCLUDES[@]}" \
  -e "$RSYNC_RSH" \
  ./ "${DEPLOY_HOST}:${DEPLOY_PATH}/"

if [[ "$DRY_RUN" == true ]]; then
  echo "Dry-run: salto compose remoto (--dry-run)." >&2
  exit 0
fi

if [[ "$UPLOAD_ENV_PROD" == true ]]; then
  if [[ ! -f "$ROOT/.env.prod" ]]; then
    echo "Manca $ROOT/.env.prod locale — non posso usarlo con --upload-env-prod." >&2
    exit 1
  fi
  echo "scp .env.prod → ${DEPLOY_HOST}:${DEPLOY_PATH}/.env.prod"
  scp "${SSH_OPTS[@]}" "$ROOT/.env.prod" "${DEPLOY_HOST}:${DEPLOY_PATH}/.env.prod"
fi

path_q=$(printf '%q' "$DEPLOY_PATH")
if [[ "${USE_SUDO_DOCKER:-false}" == "true" ]]; then
  compose_remote="sudo docker compose"
else
  compose_remote="docker compose"
fi

# Interpolazione \${VELORA_PUBLIC_HOST} in docker-compose.vps.yml: usa --env-file .env.prod sulla VPS.
echo "Compose remoto (${compose_remote})…"
# shellcheck disable=SC2029
ssh "${SSH_OPTS[@]}" "$DEPLOY_HOST" \
  "cd ${path_q} && \\
   if [[ ! -f .env.prod ]]; then \\
     echo 'ERRORE: manca ${DEPLOY_PATH}/.env.prod sul server.' >&2; \\
     echo '  Prima volta: dall host (root repo)' >&2; \\
     echo '    scp .env.prod.example '${DEPLOY_HOST}':'${DEPLOY_PATH}'/.env.prod' >&2; \\
     echo '  poi ssh sulla VPS ed imposta segreti e VELORA_PUBLIC_HOST=FQDN,' >&2; \\
     echo '  oppure, se hai già .env.prod in locale (gitignored):' >&2; \\
     echo '    ./scripts/deploy-vps.sh --upload-env-prod' >&2; \\
     exit 1; \\
   fi && \\
   if ! grep -q '^VELORA_PUBLIC_HOST=' .env.prod 2>/dev/null; then echo 'ATTENZIONE: in .env.prod manca VELORA_PUBLIC_HOST=<FQDN>.' >&2; fi && \\
   ${compose_remote} --env-file .env.prod -f docker-compose.prod.yml -f docker-compose.vps.yml build --no-cache && \\
   ${compose_remote} --env-file .env.prod -f docker-compose.prod.yml -f docker-compose.vps.yml up -d --force-recreate --remove-orphans"
echo "Fatto."

if [[ -n "${DOMAIN:-}" ]]; then
  echo "Smoke HTTPS (facoltativo, richiede curl): curl -fsSI https://${DOMAIN}/"
fi
