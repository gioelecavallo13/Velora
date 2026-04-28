# Infrastruttura Velora UI

Documento operativo dell'infrastruttura del progetto. Copre l'ambiente di sviluppo locale (Docker + virtual host `velora.local`) e quello di produzione (Docker + gunicorn + nginx + postgres).

---

## 1. Prerequisiti

Sulla macchina di sviluppo devono essere installati:

- Un runtime Docker compatibile con `docker compose` v2:
  - **Colima** (consigliato su macOS, leggero, OSS) — installazione: `brew install colima docker docker-compose`
  - oppure **Docker Desktop** >= 24
- **git** >= 2.30
- Permessi di amministratore per modificare il file `hosts` del sistema

Verifica veloce:

```bash
docker --version
docker compose version
git --version

# Solo se usi Colima:
colima version
```

### 1.1 Avvio del runtime Docker

#### Con Colima (macOS, configurazione standard di questo progetto)

Colima e` un VM Linux leggero che espone un Docker daemon. Va avviato una volta per sessione di lavoro (resta su finche` non lo fermi o riavvii il Mac):

```bash
# Primo avvio o se la VM e` spenta
colima start

# Verifica che il daemon risponda
docker info | head -5

# Quando hai finito la sessione di lavoro
colima stop
```

Note operative su Colima:

- Per default Colima alloca 2 CPU e 2 GB RAM. Per Velora (Django + nginx + node assets in parallelo) consigliato almeno: `colima start --cpu 4 --memory 6`
- Se ottieni errori di binding sulla porta 80, verifica che nessun altro processo la stia usando (vedi sezione 4 troubleshooting)
- Lo status si controlla con `colima status`

#### Con Docker Desktop

Aprire l'app Docker Desktop e attendere che l'icona (balena nella barra del menu) diventi verde / "Engine running".

---

## 2. Setup iniziale (una tantum)

### 2.1 Clonare il repository

Il repository e` privato. Per clonarlo serve essere autenticati su GitHub con un account che ha accesso a `gioelecavallo13/Velora`:

```bash
git clone git@github.com:gioelecavallo13/Velora.git
cd Velora
```

### 2.2 Creare il file `.env` locale

Copiare il template e adattare se necessario (i valori di default funzionano in dev):

```bash
cp .env.example .env
```

Il file `.env` e` ignorato da git (`.gitignore`). Non committarlo mai.

### 2.3 Aggiungere `velora.local` al file hosts

Per accedere all'app via `http://velora.local` invece di `http://localhost` serve risolvere il nome dominio sull'IP di loopback `127.0.0.1`. La modifica del file hosts e` un'operazione una tantum, fatta sulla macchina dello sviluppatore.

#### macOS / Linux

```bash
sudo sh -c 'printf "\n127.0.0.1   velora.local\n" >> /etc/hosts'
```

In alternativa, aprire il file con un editor:

```bash
sudo nano /etc/hosts
```

e aggiungere la riga:

```text
127.0.0.1   velora.local
```

#### Windows

1. Aprire il Blocco Note come Amministratore
2. Aprire il file `C:\Windows\System32\drivers\etc\hosts`
3. Aggiungere in fondo: `127.0.0.1   velora.local`
4. Salvare

#### Verifica

```bash
ping -c 1 velora.local
# Deve rispondere da 127.0.0.1
```

Se il browser non risolve subito, svuotare la cache DNS:

- macOS: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`
- Linux (systemd): `sudo systemd-resolve --flush-caches`
- Windows: `ipconfig /flushdns`

---

## 3. Avvio ambiente di sviluppo

Se usi Colima, **prima** avvia la VM:

```bash
colima start                # oppure: colima start --cpu 4 --memory 6
```

Poi, comando standard per l'app:

```bash
docker compose -f docker-compose.dev.yml up
```

Servizi avviati:

| Servizio | Ruolo | Porta |
|---|---|---|
| `web` | Django dev server (`runserver` con autoreload), pacchetto `velora_ui` in modalita` editable | `8000` (interna) |
| `assets` | Container Node placeholder, ospitera` la pipeline `dart-sass --watch` + `esbuild --watch` (configurata in Fase 3 / M1) | nessuna porta esposta |
| `nginx` | Reverse proxy verso `web`, virtual host `velora.local` | `80` (esposta sull'host) |

Quando i container sono pronti:

- App: **http://velora.local**

Output atteso al primo accesso: pagina placeholder dello showcase con badge versione `v0.0.1`.

### 3.1 Comandi utili

```bash
# Avvio in foreground (default, log a schermo)
docker compose -f docker-compose.dev.yml up

# Avvio in background (detached)
docker compose -f docker-compose.dev.yml up -d

# Stop senza eliminare i volumi
docker compose -f docker-compose.dev.yml down

# Stop e pulizia completa (cancella database SQLite ed eventuali volumi nominati)
docker compose -f docker-compose.dev.yml down -v

# Shell nel container web
docker compose -f docker-compose.dev.yml exec web bash

# Esecuzione di un comando Django one-shot
docker compose -f docker-compose.dev.yml exec web python manage.py migrate
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
docker compose -f docker-compose.dev.yml exec web pytest

# Tail dei log di un singolo servizio
docker compose -f docker-compose.dev.yml logs -f web
docker compose -f docker-compose.dev.yml logs -f nginx
```

### 3.2 Rebuild dell'immagine

Quando cambia `pyproject.toml` o il `Dockerfile.dev`:

```bash
docker compose -f docker-compose.dev.yml build web
docker compose -f docker-compose.dev.yml up -d
```

---

## 4. Troubleshooting

### Porta 80 occupata

Se nginx non parte con un errore `bind: address already in use` significa che un altro processo sta gia` ascoltando sulla porta 80 (es. un altro nginx, Apache, Skype legacy).

Soluzioni:

1. Fermare il processo conflittuale.
2. Oppure cambiare temporaneamente la porta in `docker-compose.dev.yml`, sezione `nginx.ports`, da `"80:80"` a `"8080:80"`. In quel caso pero` l'URL diventa `http://velora.local:8080` e non `http://velora.local`.

### `velora.local` non viene risolto

- Verificare che la riga `127.0.0.1   velora.local` sia effettivamente presente nel file hosts (vedi sezione 2.3)
- Svuotare la cache DNS del sistema operativo
- In Chrome, andare su `chrome://net-internals/#dns` e cliccare "Clear host cache"

### Permessi negati su `entrypoint.sh`

Lo script deve essere eseguibile. Se git non preserva il bit di esecuzione:

```bash
chmod +x docker/entrypoint.sh
docker compose -f docker-compose.dev.yml build web
```

### Database "no such table"

Probabilmente le migrate non sono state applicate nel volume corrente:

```bash
docker compose -f docker-compose.dev.yml exec web python manage.py migrate
```

In alternativa azzerare il volume dati e ricominciare:

```bash
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up
```

---

## 5. Ambiente di produzione

Lo stack di produzione vive in `docker-compose.prod.yml` ed e` separato per intero da quello di sviluppo: file diverso, Dockerfile diverso (`docker/Dockerfile.prod` multi-stage), `.env.prod` distinto, immagini buildate con tag dedicato.

### 5.1 Architettura

| Servizio | Immagine | Ruolo |
|---|---|---|
| `db` | `postgres:16-alpine` | database, volume nominato `pgdata`, healthcheck `pg_isready` |
| `web` | build da `docker/Dockerfile.prod` (multi-stage: `node:20-alpine` per asset → `python:3.11-slim` runtime non-root) | Django + gunicorn |
| `nginx` | `nginx:alpine` | reverse proxy, serving `/static/` e `/media/` da volumi condivisi, gzip, header sicurezza, TLS-ready |

I volumi nominati `pgdata`, `staticfiles`, `media` persistono fra `down` e `up`. Per cancellarli serve `docker compose down -v`.

### 5.2 Setup iniziale

```bash
# 1. Generare il file .env.prod a partire dal template
cp .env.prod.example .env.prod

# 2. Generare una SECRET_KEY robusta (mai riusare quella di dev!)
python -c "import secrets; print(secrets.token_urlsafe(64))"
# copiare il risultato in DJANGO_SECRET_KEY del .env.prod

# 3. Impostare le credenziali postgres (POSTGRES_PASSWORD obbligatorio)
#    e adattare DATABASE_URL di conseguenza.

# 4. Aggiornare DJANGO_ALLOWED_HOSTS con il dominio reale
#    (es. velora.example.com). Senza un valore valido Django risponde 400.
```

Verifica che `.env.prod` sia ignorato da git: `git check-ignore .env.prod` deve stamparne il path.

### 5.3 Build e avvio

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Cosa succede in ordine:

1. `db` parte e diventa healthy quando `pg_isready` risponde.
2. `web` viene buildato (stage 1: build asset SCSS/JS con `dart-sass`+`esbuild`; stage 2: install pacchetto e collectstatic). Aspetta `db` healthy.
3. L'entrypoint dentro `web` esegue: `python manage.py migrate --noinput`, `python manage.py collectstatic --noinput`, poi `gunicorn` con `${GUNICORN_WORKERS}` workers, timeout `${GUNICORN_TIMEOUT}s`, riavvio graceful ogni `${GUNICORN_MAX_REQUESTS}` richieste (vedi `docker/entrypoint.sh`).
4. `nginx` si lega alla porta `${NGINX_HTTP_PORT:-80}` dell'host, fa proxy a `web:8000` per `/`, serve direttamente `/static/` e `/media/` dai volumi.

### 5.4 Smoke test post-deploy

```bash
# stato dei container e healthcheck
docker compose -f docker-compose.prod.yml ps

# log di gunicorn (deve vedere "Booting worker")
docker compose -f docker-compose.prod.yml logs web --tail 50

# raggiungibilita` HTTP via nginx (sostituire la porta se hai cambiato NGINX_HTTP_PORT)
curl -I http://localhost/
# deve rispondere "HTTP/1.1 200 OK" o "302 Found" verso la home

# verifica che gli asset statici vengano serviti da nginx (non da gunicorn)
curl -I http://localhost/static/velora_ui/css/dist/velora.css
# deve rispondere 200 con header "Cache-Control: public, must-revalidate"
```

### 5.5 Backup e ripristino database

```bash
# Backup full (custom format, compresso)
docker compose -f docker-compose.prod.yml exec -T db \
    pg_dump -U "${POSTGRES_USER:-velora}" -d "${POSTGRES_DB:-velora}" -Fc \
    > "backups/velora_$(date +%Y%m%d_%H%M).dump"

# Ripristino in un db vuoto (azzerare prima):
docker compose -f docker-compose.prod.yml exec -T db \
    pg_restore -U "${POSTGRES_USER:-velora}" -d "${POSTGRES_DB:-velora}" --clean --if-exists \
    < backups/velora_20260428_1800.dump
```

Pianificare un cron host per snapshot regolari su disco esterno o storage cloud.

### 5.6 Rotazione dei log

Per default i log di `gunicorn` vanno su stdout/stderr e vengono catturati dal log driver di Docker. Su una macchina singola:

```bash
# vedere i log di tutti i servizi
docker compose -f docker-compose.prod.yml logs -f --tail 200

# limitare la dimensione dei file di log (json-file driver):
# in /etc/docker/daemon.json
# {"log-driver": "json-file", "log-opts": {"max-size": "50m", "max-file": "5"}}
# poi: sudo systemctl restart docker
```

In ambienti gestiti (k8s, Nomad, etc.) si delega a un sidecar (loki, fluentbit, ...).

### 5.7 Aggiornamento (deploy di una nuova versione)

```bash
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build web nginx
```

Il pattern `up -d --build <servizio>` ricostruisce solo i container necessari mantenendo `db` con i suoi dati. Il primo accesso post-deploy applica `migrate` e `collectstatic` automaticamente (vedi entrypoint).

### 5.8 Attivazione TLS (LetsEncrypt)

Quando il dominio e` pubblico e i record DNS sono propagati:

1. Decommentare il blocco `server { listen 443 ssl ... }` in `docker/nginx/prod.conf` e il `redirect 80 → 443`.
2. Decommentare `- "${NGINX_HTTPS_PORT:-443}:443"` e il volume `/etc/letsencrypt:/etc/letsencrypt:ro` in `docker-compose.prod.yml`.
3. Decommentare `add_header Strict-Transport-Security ...` in `prod.conf` (DOPO che HTTPS funziona end-to-end, altrimenti i browser pinnano un certificato invalido).
4. Ottenere il certificato (esempio con `certbot --nginx` o `certbot certonly --webroot`); seguire la documentazione del provider.

---

## 6. Separazione netta dev / prod

| Aspetto | Dev | Prod |
|---|---|---|
| Compose file | `docker-compose.dev.yml` | `docker-compose.prod.yml` |
| Dockerfile | `docker/Dockerfile.dev` (single-stage) | `docker/Dockerfile.prod` (multi-stage, utente non-root) |
| Server | `runserver` con autoreload | `gunicorn` |
| Database | SQLite file in volume | Postgres 16 in container |
| Source mount | si` (hot reload) | no (build immutabile) |
| Asset watcher | container `assets` con sass+esbuild watch | asset compilati nello stage builder |
| Reverse proxy | nginx con `velora.local` | nginx con dominio produzione, TLS-ready |
| Env file | `.env` | `.env.prod` |
| Variabile chiave | `DJANGO_DEBUG=1` | `DJANGO_DEBUG=0` |
