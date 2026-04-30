# Velora UI

[![status: pre-alpha](https://img.shields.io/badge/status-pre--alpha-orange)](#stato-progetto)
[![python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![django](https://img.shields.io/badge/django-5.x-092e20)](pyproject.toml)
[![license](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

**Velora UI** e` un framework grafico Django pensato per pannelli admin e gestionali interni. Espone template tag riusabili, un design system SCSS sobrio ad alta densita` informativa, JavaScript vanilla a moduli ES e una infrastruttura Docker pronta all'uso (sviluppo + produzione).

L'obiettivo e` consegnare componenti consistenti — header, sidebar, form, tabelle, link e feedback — senza dipendenze runtime sul frontend e senza lock-in su framework JavaScript.

---

## Indice

- [Caratteristiche v0.1](#caratteristiche-v01)
- [Quickstart sviluppo](#quickstart-sviluppo)
- [Consumo solo asset Web (HTML / CSS / JS)](#consumo-solo-asset-web-html--css--js)
- [Installazione in un progetto Django](#installazione-in-un-progetto-django)
- [Componenti disponibili](#componenti-disponibili)
- [Showcase / living styleguide](#showcase--living-styleguide)
- [Test](#test)
- [Sviluppo con Docker](#sviluppo-con-docker)
- [Roadmap](#roadmap)
- [Stato progetto](#stato-progetto)
- [Licenza](#licenza)

---

## Caratteristiche v0.1

- **Layout core**: header con link e user-menu, sidebar collassabile, title bar con azioni primarie/secondarie, base.html riusabile.
- **Form core**: `velora_form_row` con dispatch su 7 tipi base (text, textarea, select, checkbox, radio, on/off, file), `velora_search_box`, `velora_fields_separator`. Widget custom `OnOffWidget` integrato.
- **Tabelle e link**: `velora_table` con normalizzazione header/righe e `empty_message`, `velora_pagination` (compatibile con `Page` di Django), 4 link essenziali (`velora_action_link` arancio, `velora_nav_link` blu, `velora_delete_link` rosso con conferma, `velora_btn_link` button-styled).
- **Feedback**: `velora_alert` (4 varianti, dismissible), `velora_label` (5 varianti badge), `velora_toast_messages` che integra `django.contrib.messages` con il sistema toast JS.
- **Design system**: tokens SCSS (palette, tipografia, spacing) come CSS custom properties, predisposti per dark mode futura.
- **Infrastruttura Docker**: `docker compose up` avvia Django + nginx + watcher asset, virtual host locale `velora.local`, separazione netta `.env` (dev) / `.env.prod` (prod) con gunicorn + postgres + nginx in produzione.
- **Living styleguide**: app `showcase` documenta visualmente ogni componente con render live + snippet. Visual regression con Playwright contro 7 baseline PNG.

---

## Quickstart sviluppo

Prerequisiti: [Colima](https://github.com/abiosoft/colima) (consigliato su macOS) o Docker Desktop, git, e permessi amministratore per modificare il file hosts.

```bash
# 1. Avviare il runtime Docker (esempio con Colima)
colima start --cpu 4 --memory 6

# 2. Clonare il repository
git clone git@github.com:gioelecavallo13/Velora.git
cd Velora

# 3. Configurare l'ambiente locale
cp .env.example .env

# 4. Aggiungere velora.local al file hosts (una tantum)
sudo sh -c 'printf "\n127.0.0.1   velora.local\n" >> /etc/hosts'

# 5. Avviare lo stack (Django + asset watcher + nginx)
docker compose -f docker-compose.dev.yml up
```

A primo accesso lo showcase risponde su <http://velora.local> entro ~30 secondi (build immagine inclusa). Fonti complete nel file [`docs/INFRASTRUCTURE.md`](docs/INFRASTRUCTURE.md).

---

## Consumo solo asset Web (HTML / CSS / JS)

Per siti o applicazioni **senza** Django, gli asset ufficiali sono pubblicati **solo** come allegati delle **GitHub Releases** (tag `vX.Y.Z`):

- **CSS:** `velora-X.Y.Z.min.css`
- **JS core** (leggero, senza Chart.js): `velora-X.Y.Z.min.js`
- **JS full** (con grafici da tabella / Chart.js): `velora-X.Y.Z.full.min.js`

Esempio base:  
`https://github.com/gioelecavallo13/Velora/releases/download/vX.Y.Z/velora-X.Y.Z.min.css`

Istruzioni dettagliate, auth per repository privati, pinning e note su ESM sono in [`docs/INTEGRATION_STATIC.md`](docs/INTEGRATION_STATIC.md). Non usare il branch `main` come sorgente di produzione per questi file.

---

## Installazione in un progetto Django

Velora UI e` distribuito come pacchetto Python via Git privato. Per integrarlo in un progetto esistente:

```bash
pip install "velora-ui @ git+https://github.com/gioelecavallo13/Velora.git@v0.8.0"
```

Gli stessi tag `v0.8.0` pubblicano anche gli **asset Web** (`.min.css` / `.min.js`) sulla relativa GitHub Release: vedi [`docs/INTEGRATION_STATIC.md`](docs/INTEGRATION_STATIC.md) se ti servono solo i file statici.

Poi nel `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "velora_ui",
]

TEMPLATES = [
    {
        # ...
        "OPTIONS": {
            "context_processors": [
                # ...
                "velora_ui.context_processors.header_defaults",
            ],
        },
    },
]

# Personalizzazione opzionale di brand
VELORA_HEADER_APP_NAME = "Il mio gestionale"
VELORA_HEADER_APP_ICON_URL = "/static/img/logo.svg"

# Opzionale: carica CSS/JS dalla stessa GitHub Release (prefisso download, solo https + github.com)
# VELORA_ASSETS_BASE_URL = "https://github.com/TUO_ORG/Velora/releases/download/v0.8.0/"
# VELORA_ASSETS_JS_FULL = True   # False per bundle core senza Chart.js
```

In un template:

```django
{% extends "velora_ui/base.html" %}
{% load velora_layout velora_forms velora_data velora_links velora_feedback %}

{% block title %}Clienti{% endblock %}

{% block title_bar %}
  {% velora_title_bar title="Clienti" actions=page_actions %}
{% endblock %}

{% block content %}
  {% velora_search_box placeholder="Cerca cliente..." %}
  {% velora_table headers=table_headers rows=table_rows empty_message="Nessun cliente trovato" %}
  {% velora_pagination page=page_obj %}
{% endblock %}
```

I contratti dettagliati di ogni tag (chiavi accettate dei dict in input, comportamento con valori mancanti) sono in [`AGENTS.md`](AGENTS.md).

---

## Componenti disponibili

| Modulo | Tag | Scopo |
|---|---|---|
| `velora_assets` | `{% velora_assets %}` | Inietta CSS + JS compilati con cache-busting |
| `velora_layout` | `{% velora_header items=... %}` | Header globale (link + user-menu) |
| `velora_layout` | `{% velora_title_bar title=... actions=... %}` | Title bar di pagina con CTA |
| `velora_forms` | `{% velora_form_row type=... name=... ... %}` | Form row dispatcher (7 tipi base) |
| `velora_forms` | `{% velora_search_box %}` | Barra di ricerca semplice |
| `velora_forms` | `{% velora_fields_separator %}` | Separatore visivo fra gruppi di campi |
| `velora_data` | `{% velora_table headers=... rows=... %}` | Tabella statica con header/rows normalizzati |
| `velora_data` | `{% velora_pagination page=... %}` | Paginazione con preservazione querystring |
| `velora_links` | `{% velora_action_link href=... label=... %}` | Link arancio per azioni di riga |
| `velora_links` | `{% velora_nav_link href=... label=... %}` | Link blu per navigazione |
| `velora_links` | `{% velora_delete_link href=... label=... %}` | Link rosso con `window.confirm()` JS |
| `velora_links` | `{% velora_btn_link href=... label=... variant=... %}` | Link stilizzato come pulsante |
| `velora_feedback` | `{% velora_alert variant=... %}...{% endvelora_alert %}` | Alert inline (4 varianti) |
| `velora_feedback` | `{% velora_label variant=... text=... %}` | Badge inline (5 varianti) |
| `velora_feedback` | `{% velora_toast_messages %}` | Bridge `django.contrib.messages` → toast JS |

API JS pubblica esposta su `window.Velora`:

- `Velora.toast.success(text, opts)` / `error` / `warning` / `info` / `show({variant, message, duration, persistent, dismissible})` / `dismissAll()`
- `Velora.register({name, init})` per agganciare componenti custom al sistema di auto-init via `MutationObserver`

---

## Showcase / living styleguide

L'app `showcase` (in `showcase/`) e` la documentazione visuale viva di Velora UI. Una volta avviato lo stack dev, la pagina <http://velora.local> mostra ogni componente con:

- render live con dati realistici
- snippet copiabile del codice template
- sidebar TOC navigabile fra le 6 sezioni (overview, layout, form, tabelle, link, feedback)

La consistenza grafica e` protetta da test di visual regression Playwright (`tests/visual/`) con 7 baseline PNG (uno per sezione + uno full page). Quando un componente cambia di proposito, le baseline si aggiornano con `pytest tests/visual --update-snapshots`.

---

## Test

Suite pytest unitaria (template tag, widget, context processor):

```bash
docker compose -f docker-compose.dev.yml exec web pytest
```

Visual regression (in container dedicato `playwright-tests` con browser pre-installati):

```bash
# confronto contro baseline (CI mode)
docker compose -f docker-compose.dev.yml --profile test run --rm playwright-tests

# rigenerare le baseline (dopo cambio voluto)
docker compose -f docker-compose.dev.yml --profile test run --rm playwright-tests \
  bash -lc "pip install --quiet --ignore-requires-python -e .[dev] && pytest tests/visual --update-snapshots"
```

Stato attuale: **236** test unitari + **17** snapshot Playwright (16 sezioni + 1 full page), tutti verdi dopo aggiornamento baseline quando necessario.

Prima di generare gli asset Ionicons nello showcase: `npm install` e `npm run sync:icons` (copia le SVG da `ionicons` e rigenera `ionicons-manifest.json`).

---

## Sviluppo con Docker

Lo stack di sviluppo e` documentato per esteso in [`docs/INFRASTRUCTURE.md`](docs/INFRASTRUCTURE.md):

- prerequisiti e installazione runtime (Colima / Docker Desktop)
- setup `velora.local` su macOS / Linux / Windows
- comandi utili (shell, migrate, createsuperuser, logs, rebuild)
- troubleshooting (porta 80 occupata, DNS, migrazioni, permessi)
- separazione completa dev / prod
- deploy produzione con `docker-compose.prod.yml` (gunicorn + nginx + postgres + TLS-ready)

---

## Roadmap

| Versione | Stato | Contenuto principale |
|---|---|---|
| v0.1.0 | rilasciato | Layout, form 7 tipi base, tabella + paginazione, 4 link, feedback, showcase, Docker dev+prod |
| v0.2.0 | rilasciato | Header multi-menu/apps-menu/notifications, breadcrumb, tooltip, submenu, dropdown, dialog, copy/toggle/settings link, progress bar (3 varianti) |
| **v0.3.0** | rilasciato | Form avanzati (datepicker, datetimepicker, multiselect, autocomplete locale + remoto, image_preview, rating_stars, timer_fields, redactor), tabelle interattive con form-in-cell AJAX e bulk-actions, checkbox tag con 5 varianti colore |
| **v0.4.0** | rilasciato | Chart.js da tabella, sync Ionicons + galleria showcase, `velora_logo`, `velora_satisfaction_bar`, tema dark CSS, i18n (IT/EN showcase) |
| **v0.5.0** | in release | Asset Web su GitHub Releases (core/full), `INTEGRATION_STATIC` + snippet, CI release + pytest, `ui_registry` SSoT, opzionale `VELORA_ASSETS_BASE_URL` |
| **v0.8.0** | in release | Allineamento versione (Python/npm/JS runtime), showcase (classi CSS, chart da `velora_table`, stile Chart.js), toast come alert, dropdown e form avanzati |

Dettagli e milestone in [`velora-ui_django_framework_61f8855e.plan.md`](.cursor/plans/velora-ui_django_framework_61f8855e.plan.md) (cartella piani locale).

---

## Stato progetto

Versione corrente: vedi [`pyproject.toml`](pyproject.toml). Le release alpha (`v0.1.0-alpha.x`) hanno chiuso le milestone M1 → M5 di v0.1; la release candidate `v0.1.0-rc.1` ha chiuso M6. La v0.1.0 stabile ha chiuso M7. La v0.2.0 ha chiuso la Fase 10 del piano (navigation e feedback ricchi). La v0.3.0 chiude la Fase 11: form avanzati & tabelle interattive. La v0.4.0 chiude la Fase 12 del piano: chart da tabella, Ionicons, logo/satisfaction, tema dark, i18n. La v0.5.0 aggiunge distribuzione asset Web via GitHub Releases, documentazione statica e integrazione Django opzionale sugli stessi URL. Il progetto e` distribuito via Git privato, non e` ancora pubblicato su PyPI.

Le decisioni di prodotto (target, distribuzione, criteri di successo) sono tracciate in [`VISION.md`](VISION.md).

---

## Licenza

Velora UI e` rilasciato con [Apache License 2.0](LICENSE).
