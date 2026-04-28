#!/usr/bin/env sh
# Entrypoint del container `assets` di docker-compose.dev.yml.
#
# Eseguito sequenzialmente:
#   1. npm install delle devDependencies (sass + esbuild) nel volume nominato
#      `velora-node-modules` (cache fra restart)
#   2. one-shot build di CSS e JS, cosi` i file esistono sul disco quando
#      web li serve via STATICFILES_DIRS
#   3. avvio in parallelo dei due watcher (sass --watch + esbuild --watch)
#      con `wait` finale: se uno dei due muore, lo script termina e il
#      container viene riavviato dal restart policy di compose
#
# Lo script vive come file separato perche` mettere logica multi-linea con `&`
# in un `command:` YAML folded scalar (`>`) confonde la semantica della shell
# (il `&` finisce sulla stessa riga del comando successivo, e il watcher JS
# parte in foreground prima che npm install completi). Estraendo qui ce
# l'abbiamo robusto e debuggabile.

set -eu

echo "[velora-assets] npm install (cache: volume velora-node-modules)"
npm install --silent

echo "[velora-assets] one-shot build CSS + JS"
sh tools/build_css.sh build
sh tools/build_js.sh build

echo "[velora-assets] starting watchers (sass + esbuild in parallel)"
sh tools/build_css.sh watch &
PID_CSS=$!
sh tools/build_js.sh watch &
PID_JS=$!

trap 'echo "[velora-assets] shutdown, killing watchers"; kill ${PID_CSS} ${PID_JS} 2>/dev/null || true' INT TERM

wait
