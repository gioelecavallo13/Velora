# Infrastruttura Velora UI

Documento operativo dell'infrastruttura del progetto. Copre l'ambiente di sviluppo locale (Docker + virtual host `velora.local`) e quello di produzione (Docker + gunicorn + nginx + postgres).

La sezione produzione e` un placeholder strutturale fino al completamento della Fase 9 (M7 Release v0.1.0); le istruzioni complete arriveranno con quella milestone.

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

## 5. Ambiente di produzione (placeholder, completato in Fase 9)

Configurazione completa in `docker-compose.prod.yml` con servizi `web` (gunicorn), `nginx` (reverse proxy + serving static), `db` (postgres). Variabili in `.env.prod` (separate da `.env` di sviluppo). Documento aggiornato a fine M7 con istruzioni complete di deploy.

---

## 6. Separazione netta dev / prod

| Aspetto | Dev | Prod |
|---|---|---|
| Compose file | `docker-compose.dev.yml` | `docker-compose.prod.yml` (Fase 9) |
| Dockerfile | `docker/Dockerfile.dev` | `docker/Dockerfile.prod` (Fase 9) |
| Server | `runserver` con autoreload | `gunicorn` |
| Database | SQLite file in volume | Postgres 16 in container |
| Source mount | si` (hot reload) | no (build immutabile) |
| Asset watcher | container `assets` con sass+esbuild watch | asset compilati nello stage builder |
| Reverse proxy | nginx con `velora.local` | nginx con dominio produzione, TLS-ready |
| Env file | `.env` | `.env.prod` |
| Variabile chiave | `DJANGO_DEBUG=1` | `DJANGO_DEBUG=0` |
