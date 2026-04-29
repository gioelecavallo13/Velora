#!/usr/bin/env sh
# Copia le SVG Ionicons da node_modules nella static tree di velora_ui e
# genera ionicons-manifest.json (lista slug alfabetica) per la galleria showcase.
#
# Prerequisito: npm install (ionicons in devDependencies)
# Uso: sh tools/sync_ionicons.sh

set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/node_modules/ionicons/dist/ionicons/svg"
DST="$ROOT/src/velora_ui/static/velora_ui/icons/ionicons"

if [ ! -d "$SRC" ]; then
  echo "[sync_ionicons] errore: $SRC non trovato. Esegui: npm install" >&2
  exit 1
fi

mkdir -p "$DST"
cp "$SRC"/*.svg "$DST/"
COUNT=$(find "$DST" -maxdepth 1 -name "*.svg" | wc -l | tr -d ' ')
echo "[sync_ionicons] copiate $COUNT icone in $DST"

python3 -c "
import json
from pathlib import Path
root = Path('$ROOT')
p = root / 'src/velora_ui/static/velora_ui/icons/ionicons'
names = sorted(x.stem for x in p.glob('*.svg'))
out = root / 'src/velora_ui/static/velora_ui/icons/ionicons-manifest.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(names, ensure_ascii=False), encoding='utf-8')
print(f'[sync_ionicons] manifest: {len(names)} slug -> {out}')
"
