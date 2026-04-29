#!/usr/bin/env sh
# Pubblica una GitHub Release e carica gli artifact da dist/ per il tag vX.Y.Z.
# Richiede GITHUB_TOKEN o GH_TOKEN (PAT con scope repo).
#
# Uso:
#   export GITHUB_TOKEN=ghp_xxxx
#   sh tools/publish_github_release_manual.sh 0.5.0

set -eu

VERSION="${1:?usage: $0 X.Y.Z}"
TAG="v${VERSION}"
REPO_SLUG="${GITHUB_REPOSITORY:-gioelecavallo13/Velora}"
API="https://api.github.com/repos/${REPO_SLUG}"

if test -z "${GITHUB_TOKEN:-}" && test -z "${GH_TOKEN:-}"; then
  echo "Imposta GITHUB_TOKEN o GH_TOKEN (PAT con permesso repo)." >&2
  exit 1
fi
TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-}}"

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PY='import json,sys; print(json.dumps({"tag_name":sys.argv[1],"name":sys.argv[1],"body":sys.argv[2],"draft":False,"prerelease":False}))'
BODY="Release manuale **${VERSION}**: asset Web + wheel/sdist, allineati al tag \`${TAG}\`. Build locale."
JSON_PAYLOAD="$(python3 -c "$PY" "$TAG" "$BODY")"

collect_files() {
  for f in \
    "dist/velora-${VERSION}.min.css" \
    "dist/velora-${VERSION}.min.css.map" \
    "dist/velora-${VERSION}.min.js" \
    "dist/velora-${VERSION}.min.js.map" \
    "dist/velora-${VERSION}.full.min.js" \
    "dist/velora-${VERSION}.full.min.js.map" \
    "dist/velora_ui-${VERSION}-py3-none-any.whl" \
    "dist/velora_ui-${VERSION}.tar.gz"
  do
    if test ! -f "$f"; then
      echo "Manca: $f — esegui npm run build:web && python3 -m build (da venv con build)" >&2
      exit 1
    fi
    echo "$f"
  done
}

FILES="$(collect_files)"

echo "Creo release $TAG su $REPO_SLUG..."
CREATE_JSON="$(curl -sS -w '\n%{http_code}' -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "$API/releases" \
  -d "$JSON_PAYLOAD")"

HTTP_CODE="$(echo "$CREATE_JSON" | tail -n1)"
CREATE_BODY="$(echo "$CREATE_JSON" | sed '$d')"

if test "$HTTP_CODE" = "201"; then
  UPLOAD_URL_TEMPLATE="$(echo "$CREATE_BODY" | python3 -c 'import json,sys; print(json.load(sys.stdin)["upload_url"])')"
elif test "$HTTP_CODE" = "422"; then
  echo "Release potrebbe esistere già; provo GET by tag..."
  REL_JSON="$(curl -sS -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" "$API/releases/tags/$TAG")"
  UPLOAD_URL_TEMPLATE="$(echo "$REL_JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("upload_url",""))')"
  if test -z "$UPLOAD_URL_TEMPLATE" || test "$UPLOAD_URL_TEMPLATE" = "None"; then
    echo "Errore: $CREATE_BODY" >&2
    exit 1
  fi
  echo "Nota: upload su release esistente (stessi nomi file = errore su duplicati)."
else
  echo "HTTP $HTTP_CODE — $CREATE_BODY" >&2
  exit 1
fi

for f in $FILES; do
  name="$(basename "$f")"
  base="${UPLOAD_URL_TEMPLATE%\{*}"
  url="${base}?name=${name}"
  echo "Upload $name..."
  UP_RESP="$(curl -sS -w '\n%{http_code}' -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Accept: application/vnd.github+json" \
    -H "Content-Type: application/octet-stream" \
    --data-binary "@$f" \
    "$url")"
  UP_CODE="$(echo "$UP_RESP" | tail -n1)"
  if test "$UP_CODE" != "201"; then
    echo "Upload fallito $name HTTP $UP_CODE" >&2
    echo "$UP_RESP" | sed '$d' >&2
    exit 1
  fi
done

echo "OK: release $TAG con allegati pubblicati."
