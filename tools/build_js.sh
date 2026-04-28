#!/usr/bin/env sh
# Build script per il JavaScript di Velora UI.
# Bundle src/velora_ui/static/velora_ui/js/src/velora.js in
# src/velora_ui/static/velora_ui/js/velora.js (ESM, ES2020, sourcemap).
#
# Uso:
#   sh tools/build_js.sh           # one-shot build (default)
#   sh tools/build_js.sh build     # one-shot build (esplicito)
#   sh tools/build_js.sh watch     # watch mode
#
# Il binario `esbuild` viene cercato in node_modules/.bin/. Per overridare
# (es. test in locale con esbuild globale) impostare la variabile ESBUILD_BIN.

set -eu

ESBUILD_BIN="${ESBUILD_BIN:-node_modules/.bin/esbuild}"
INPUT="src/velora_ui/static/velora_ui/js/src/velora.js"
OUTPUT="src/velora_ui/static/velora_ui/js/velora.js"
MODE="${1:-build}"

if [ ! -x "$ESBUILD_BIN" ] && ! command -v "$ESBUILD_BIN" > /dev/null 2>&1; then
    echo "[build_js] errore: binario esbuild non trovato in $ESBUILD_BIN" >&2
    echo "[build_js] in container assets esegui prima 'npm install'." >&2
    exit 1
fi

COMMON_ARGS="--bundle --outfile=$OUTPUT --sourcemap --target=es2020 --format=esm"

case "$MODE" in
    watch)
        # `--watch=forever` evita che esbuild esca con
        # "[watch] stopped automatically because stdin was closed" quando lo
        # eseguiamo dentro un container detached (senza tty).
        echo "[build_js] watch: $INPUT -> $OUTPUT"
        exec "$ESBUILD_BIN" "$INPUT" $COMMON_ARGS --watch=forever
        ;;
    build|*)
        echo "[build_js] build: $INPUT -> $OUTPUT"
        exec "$ESBUILD_BIN" "$INPUT" $COMMON_ARGS
        ;;
esac
