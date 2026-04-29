# Fase 1.3 piano deploy: copiare in env-exports.sh (opzionale, gitignored) oppure fare source inline.
#   cp scripts/env-exports.example.sh scripts/env-exports.sh
# poi: source scripts/env-exports.sh

export VPS_HOST="${VPS_HOST:-203.0.113.10}"
export DOMAIN="${DOMAIN:-velora.example.com}"
