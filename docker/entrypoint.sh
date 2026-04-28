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
    echo "[velora-entrypoint] avvio gunicorn (workers=${GUNICORN_WORKERS})"
    exec gunicorn velora_project.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers "${GUNICORN_WORKERS}" \
        --access-logfile - \
        --error-logfile -
else
    echo "[velora-entrypoint] avvio runserver"
    exec python manage.py runserver 0.0.0.0:8000
fi
