#!/usr/bin/env sh
# Entrypoint condiviso fra ambiente dev e prod.
# Sceglie il server e le operazioni preliminari in base alla variabile DJANGO_ENV.
#
# - dev  : applica le migrate e avvia `runserver` con autoreload.
# - prod : applica migrate, esegue collectstatic, avvia `gunicorn` (workers parametrizzabili).

set -eu

DJANGO_ENV="${DJANGO_ENV:-dev}"

echo "[velora-entrypoint] DJANGO_ENV=${DJANGO_ENV}"

# Garantisce l'esistenza della cartella per il database SQLite in dev.
mkdir -p /app/data

echo "[velora-entrypoint] applico le migrate"
python manage.py migrate --noinput

if [ "${DJANGO_ENV}" = "prod" ]; then
    echo "[velora-entrypoint] eseguo collectstatic"
    python manage.py collectstatic --noinput

    GUNICORN_WORKERS="${GUNICORN_WORKERS:-3}"
    GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-30}"
    GUNICORN_MAX_REQUESTS="${GUNICORN_MAX_REQUESTS:-1000}"
    GUNICORN_MAX_REQUESTS_JITTER="${GUNICORN_MAX_REQUESTS_JITTER:-50}"
    echo "[velora-entrypoint] avvio gunicorn (workers=${GUNICORN_WORKERS}, timeout=${GUNICORN_TIMEOUT}s, max-requests=${GUNICORN_MAX_REQUESTS})"
    # --max-requests + jitter: ogni worker viene riciclato dopo N richieste
    #   (con offset random) per evitare memory bloat in long-run.
    # --access-logfile/--error-logfile su stdout/stderr per essere catturati
    #   da `docker logs` e dal log driver di compose/produzione.
    exec gunicorn velora_project.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers "${GUNICORN_WORKERS}" \
        --timeout "${GUNICORN_TIMEOUT}" \
        --max-requests "${GUNICORN_MAX_REQUESTS}" \
        --max-requests-jitter "${GUNICORN_MAX_REQUESTS_JITTER}" \
        --access-logfile - \
        --error-logfile -
else
    echo "[velora-entrypoint] avvio runserver"
    exec python manage.py runserver 0.0.0.0:8000
fi
