#!/usr/bin/env sh
# Build artefatti Velora Web per GitHub Releases:
#   dist/velora-{version}.min.css (+ .map)
#   dist/velora-{version}.min.js (+ .map)      — bundle **core** (senza Chart.js)
#   dist/velora-{version}.full.min.js (+ .map) — bundle **full** (con Chart.js)
#
# Versione: env VELORA_VERSION oppure lettura da src/velora_ui/__init__.py
# Richiede: npm install (sass + esbuild in node_modules)
#
# Uso: sh tools/build_web_dist.sh

set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VERSION="${VELORA_VERSION:-}"
if [ -z "$VERSION" ]; then
  VERSION=$(python3 -c "import re, pathlib, sys; m = re.search(r\"__version__\\s*=\\s*['\\\"]([^'\\\"]+)['\\\"]\", pathlib.Path('src/velora_ui/__init__.py').read_text()); sys.exit(1) if not m else print(m.group(1))")
fi

SASS_BIN="${SASS_BIN:-node_modules/.bin/sass}"
ESBUILD_BIN="${ESBUILD_BIN:-node_modules/.bin/esbuild}"

if [ ! -x "$SASS_BIN" ] && ! command -v "$SASS_BIN" >/dev/null 2>&1; then
  echo "[build_web_dist] errore: sass non trovato in $SASS_BIN — eseguire npm install." >&2
  exit 1
fi
if [ ! -x "$ESBUILD_BIN" ] && ! command -v "$ESBUILD_BIN" >/dev/null 2>&1; then
  echo "[build_web_dist] errore: esbuild non trovato in $ESBUILD_BIN — eseguire npm install." >&2
  exit 1
fi

mkdir -p dist

INPUT_SCSS="src/velora_ui/static/velora_ui/scss/velora.scss"
INPUT_JS_CORE="src/velora_ui/static/velora_ui/js/src/velora_core_entry.js"
INPUT_JS_FULL="src/velora_ui/static/velora_ui/js/src/velora.js"
OUT_CSS="dist/velora-${VERSION}.min.css"
OUT_JS_CORE="dist/velora-${VERSION}.min.js"
OUT_JS_FULL="dist/velora-${VERSION}.full.min.js"

echo "[build_web_dist] SCSS -> $OUT_CSS"
"$SASS_BIN" "$INPUT_SCSS:$OUT_CSS" --style=compressed --source-map

echo "[build_web_dist] JS core -> $OUT_JS_CORE"
"$ESBUILD_BIN" "$INPUT_JS_CORE" \
  --bundle \
  --minify \
  --outfile="$OUT_JS_CORE" \
  --sourcemap \
  --target=es2020 \
  --format=esm

echo "[build_web_dist] JS full -> $OUT_JS_FULL"
"$ESBUILD_BIN" "$INPUT_JS_FULL" \
  --bundle \
  --minify \
  --outfile="$OUT_JS_FULL" \
  --sourcemap \
  --target=es2020 \
  --format=esm

echo "[build_web_dist] OK (version=$VERSION)"
