#!/usr/bin/env sh
# Build script per il CSS di Velora UI.
# Compila src/velora_ui/static/velora_ui/scss/velora.scss in
# src/velora_ui/static/velora_ui/css/velora.css con sourcemap.
#
# Uso:
#   sh tools/build_css.sh           # one-shot build (default)
#   sh tools/build_css.sh build     # one-shot build (esplicito)
#   sh tools/build_css.sh watch     # watch mode
#
# Il binario `sass` viene cercato in node_modules/.bin/. Per overridare
# (es. test in locale con sass globale) impostare la variabile SASS_BIN.

set -eu

SASS_BIN="${SASS_BIN:-node_modules/.bin/sass}"
INPUT="src/velora_ui/static/velora_ui/scss/velora.scss"
OUTPUT="src/velora_ui/static/velora_ui/css/velora.css"
MODE="${1:-build}"

if [ ! -x "$SASS_BIN" ] && ! command -v "$SASS_BIN" > /dev/null 2>&1; then
    echo "[build_css] errore: binario sass non trovato in $SASS_BIN" >&2
    echo "[build_css] in container assets esegui prima 'npm install'." >&2
    exit 1
fi

case "$MODE" in
    watch)
        echo "[build_css] watch: $INPUT -> $OUTPUT"
        exec "$SASS_BIN" --watch "$INPUT:$OUTPUT" --style=expanded
        ;;
    build|*)
        echo "[build_css] build: $INPUT -> $OUTPUT"
        exec "$SASS_BIN" "$INPUT:$OUTPUT" --style=expanded
        ;;
esac
