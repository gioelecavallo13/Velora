# Changelog

Tutte le modifiche significative a Velora UI sono documentate in questo file.

Il formato si ispira a [Keep a Changelog](https://keepachangelog.com/) e il versionamento segue [Semantic Versioning](https://semver.org/) — pre-1.0 ogni `0.x.0` puo` introdurre breaking change documentati qui.

## [0.2.0] — 2026-04-28

Seconda release: **navigation e feedback ricchi**. Aggiunti header item interattivi (single/multi-menu, apps-menu, notifications, logo aggiuntivo), breadcrumb, submenu, drop-down inline, dialog modale (inline + remote AJAX), tooltip, toggle/copy link, settings link verde, tre varianti di progress bar.

### Aggiunto

#### Header item v0.2 (`velora_layout`)
- 5 nuovi tipi item per `velora_header`:
  - `single-menu`: trigger + dropdown panel di link, allineamento `left`/`right`.
  - `multi-menu`: mega-menu a colonne (sezioni con titolo) per categorie ricche.
  - `apps-menu`: griglia 3-colonne di app launcher con icone e colori personalizzabili (CSS custom property `--velora-app-tile-color`).
  - `notifications`: campanella + badge contatore non lette + lista notifiche con stato `is-unread`, empty state, link footer "Vedi tutte".
  - `logo`: marchio aggiuntivo inline (es. tenant, brand co-branded) con immagine + label.
- Componente JS `header-menu`: toggle apri/chiudi, click fuori chiude, ESC chiude, mutua esclusione (un solo pannello aperto), focus restore.

#### Navigation (`velora_navigation`)
- `velora_breadcrumb`: lista di link con `aria-current="page"` sull'ultimo item, separatore configurabile (default `›`).
- `velora_submenu`: lista verticale con titolo opzionale, indicatore `is-active` con border-left arancio, da inserire in pannelli laterali / card.

#### Link avanzati (`velora_links`)
- `velora_settings_link`: variante verde per azioni di configurazione.
- `velora_toggle_link`: mostra/nasconde un blocco target (`is-toggled-hidden`), alterna label `show`/`hide`, sincronizza `aria-expanded`.
- `velora_copy_link`: clipboard copy (statica via `value=` o dinamica via `target=` selector); usa `navigator.clipboard.writeText` con fallback `execCommand('copy')` per HTTP locali; integra `Velora.toast` per il feedback.
- `velora_drop_down_link` e `velora_drop_down_button`: trigger inline (link sobrio o bottone primary/secondary) con pannello di menu items; allineamento `left`/`right`.
- `velora_open_dialog_action_link`: apre un dialog modale gia` nel DOM (`target="#id"`) o scaricato via fetch (`url="..."`); size `sm`/`md`/`lg`, dialog title custom.

#### Overlays (`velora_overlays`)
- `velora_tooltip`: tag che emette **solo** gli attributi data-* (no wrapper extra) da iniettare in elementi esistenti; placement `top`/`bottom`/`left`/`right`, delay configurabile.
- Componente JS `tooltip.js`: balloon globale singolo riusato fra tutti i trigger (no leak DOM), positioning con clamp al viewport, hover/focus per mostrare e mouseleave/blur/Escape per chiudere.
- Componente JS `dropdown.js`: cugino di `header-menu` ma con geometria/casi d'uso differenti (link e button inline).
- Componente JS `dialog.js`: backdrop chiudibile via `[data-dialog-close]`, ESC chiude, focus al primo focusable post-open + restore al trigger su close, body lock via classe `velora-app--dialog-open`, dialog generati al volo rimossi su close (no accumulo DOM); fragment remoto fetched con header `X-Requested-With: XMLHttpRequest` e post-fetch `Velora.scan(body)` per inizializzare componenti del fragment.
- Componenti JS `toggle.js` e `copy.js` registrati e auto-inizializzati.

#### Progress (`velora_navigation`)
- `velora_progress_bar`: barra classica con `value`/`max`, percentuale, 5 variant (`default`/`success`/`warning`/`danger`/`info`) via CSS custom property `--velora-progress-fill`.
- `velora_condensed_progress_breadcrumb`: wizard a fasi numerate con stati `is-done` (verde + check) / `is-current` (arancio + alone) / `is-upcoming` (gray-100); `current` 1-based con clamp; step `done` cliccabili se hanno `url`.
- `velora_new_progress_bar`: contatore "X di Y" + barra; `total<=0` graceful (mostra contatore senza barra), clamp `current<=total`.

#### Showcase
- 3 nuove sezioni nello showcase (`#navigation`, `#overlays`, `#progress`) con pattern "snippet + render live".
- Sidebar TOC aggiornata con voci Navigation/Overlays/Progress.
- L'header dello showcase ora dimostra tutti i 7 tipi item v0.1+v0.2 in azione.

### Modificato

- `_normalize_header_items` validation tightened: item `link`/`user-menu` senza `label` o `url` ora vengono scartati silenziosamente (prima era documentato in AGENTS.md ma non enforced — ora codice e doc sono allineati).
- AGENTS.md: aggiunto documentation completa dei 5 nuovi item type dell'header e dei nuovi tag/library.

### Corretto

- Bug pre-esistente di v0.1.0 nello showcase: il template non aveva `{% block header %}` di override, e la view passava `showcase_header_items` invece di `velora_header_items`. L'header dello showcase non mostrava nessun item (solo brand + sidebar toggle). Aggiunto override esplicito.

### Test

- 49 test pytest aggiunti (155 totali, da 106 di v0.1):
  - `tests/test_layout.py` +19 test sui 5 nuovi item type del header.
  - `tests/test_navigation.py` (nuovo, 23 test) su breadcrumb / submenu / progress_bar / condensed_breadcrumb / new_progress_bar.
  - `tests/test_overlays.py` (nuovo, 6 test) su tooltip.
  - `tests/test_links_v02.py` (nuovo, 20 test) sui 6 nuovi link tag.
- Test playwright aggiornati con 3 nuove sezioni (navigation/overlays/progress) per un totale di 10 snapshot. Baseline esistenti rigenerate per riflettere il nuovo header.

### Note tecniche

- Tutti i pannelli dropdown (header-menu, dropdown, dialog) sono auto-inizializzati via `data-velora-component="..."`: nessun JS imperativo da scrivere lato consumer. Il `MutationObserver` esistente garantisce funzionamento anche per contenuti aggiunti dinamicamente (es. fragment dialog remoto).
- I componenti `header-menu` e `dropdown` restano file separati pur condividendo il pattern open/close/outside-click/ESC: la geometria, i bersagli e l'ergonomia d'uso sono abbastanza diversi da preferire due moduli specializzati. Quando sara` chiaro il caso d'uso comune (probabilmente in v0.3 con tooltip + dropdown + dialog) estrarremo una primitiva "popup controller".

## [0.1.0] — 2026-04-28

Prima release stabile del **core**: layout admin, form essenziali, tabella + paginazione, link, feedback, showcase con visual regression. Infrastruttura Docker dev + prod completa.

### Aggiunto

#### Design system e pipeline
- Tokens SCSS (`_tokens.scss`) come CSS custom properties: palette, tipografia, spacing, sizing — predisposti per dark mode futura.
- Reset CSS minimale e set di utilities essenziali (display, flex, spacing scala 0-8, text alignment, colori semantici).
- Pipeline build con `dart-sass` e `esbuild` (script `tools/build_css.sh`, `tools/build_js.sh`, `tools/start_assets.sh`).
- Tag `{% velora_assets %}` per iniettare CSS + JS compilati con cache busting.

#### Layout (`velora_layout`)
- `velora_ui/base.html` come template base estensibile.
- `velora_header` con tipi `link` e `user-menu`, brand configurabile via settings.
- Sidebar collassabile con stato persistito in `localStorage`.
- `velora_title_bar` con titolo e azioni (varianti `primary` / `secondary`).
- Settings di pacchetto: `VELORA_HEADER_APP_NAME`, `VELORA_HEADER_APP_ICON_URL`.
- Context processor `velora_ui.context_processors.header_defaults`.

#### Form core (`velora_forms`)
- `velora_form_row` con dispatch su 7 tipi: `text` (con sub-types email/number/password/url/tel/search), `textarea`, `select`, `checkbox`, `radio`, `onoff`, `file`.
- `velora_search_box` (input search + submit).
- `velora_fields_separator`.
- Widget custom `OnOffWidget` per integrare il toggle con `forms.Form` di Django.

#### Tabelle e link (`velora_data`, `velora_links`)
- `velora_table` con normalizzazione di header (str / dict) e rows (list / dict via `key`), `empty_message`, `colspan`.
- `velora_pagination` compatibile con `Page` del `Paginator` Django o dict equivalente; finestra con gap `…`, preserva la querystring esistente.
- 4 link essenziali: `velora_action_link` (arancio), `velora_nav_link` (blu), `velora_delete_link` (rosso, con `data-velora-component="confirm"`), `velora_btn_link` (button-styled).
- Componente JS `confirm.js`: intercetta click sui delete-link, mostra `window.confirm()`, crea form al volo con CSRF token e fa submit.
- Auto-aggiunta `rel="noopener noreferrer"` per `target="_blank"`.

#### Feedback (`velora_feedback`)
- `velora_alert` con 4 varianti (success/error/warning/info), opzioni `title` e `dismissible`.
- `velora_label` badge con 5 varianti (success/error/warning/info/neutral).
- `velora_toast_messages`: bridge dal framework `django.contrib.messages` ai toast Velora via payload JSON e componente JS `toast.js`.
- API JS `Velora.toast.{success,error,warning,info,show,dismissAll}` esposta su `window.Velora`.

#### Sistema componenti JS
- Registry `Velora.register({name, init})` con auto-init via `MutationObserver` (compatibile HTMX / Turbo).
- ES modules con esbuild, target `es2020`, format `esm`.

#### Showcase / living styleguide
- App `showcase` con pagina `/` strutturata in 6 sezioni navigabili (overview, layout, form, tabelle, link, feedback).
- Sidebar TOC che riusa `showcase_sidebar_items` con anchor scroll-margin-aware.
- Pattern `showcase-demo`: render live + snippet codice (`{% verbatim %}`) affiancati in griglia 2 colonne, stack su mobile.
- Visual regression con Playwright: `tests/visual/` con 7 baseline PNG (1 per sezione + 1 full-page) e confronto bytewise; servizio compose `playwright-tests` con immagine ufficiale Microsoft.

#### Infrastruttura

##### Sviluppo
- `docker-compose.dev.yml` con servizi `web` (Django runserver), `assets` (Node con `dart-sass --watch` + `esbuild --watch`), `nginx` (reverse proxy su `velora.local`), `playwright-tests` (profilo `test`).
- `docker/Dockerfile.dev` su `python:3.11-slim`, install editable di `velora-ui[dev]`.
- `docker/entrypoint.sh` condiviso dev/prod (branching su `DJANGO_ENV`).
- Virtual host locale `velora.local` via `docker/nginx/dev.conf`.
- `.env` / `.env.example` per configurazione locale.
- Documentazione completa in `docs/INFRASTRUCTURE.md` (prerequisiti Colima/Docker Desktop, setup hosts macOS/Linux/Windows, comandi utili, troubleshooting).

##### Produzione
- `docker-compose.prod.yml` con servizi `db` (Postgres 16-alpine + healthcheck + volume nominato `pgdata`), `web` (gunicorn da `Dockerfile.prod`, depends_on db healthy), `nginx` (reverse proxy + serving statici da volume condiviso, TLS-ready).
- `docker/Dockerfile.prod` multi-stage: stage 1 `node:20-alpine` per build asset, stage 2 `python:3.11-slim` runtime con utente non-root.
- `docker/nginx/prod.conf` con server_name da env, gzip, header di sicurezza, location `/static/` e `/media/` da volume, blocco TLS commentato pronto.
- `.env.prod.example` documentato (SECRET_KEY, ALLOWED_HOSTS, DATABASE_URL, POSTGRES_*, GUNICORN_WORKERS).
- Sezione "Deploy produzione" in `docs/INFRASTRUCTURE.md`.

#### Documentazione e qualita`
- `README.md` con quickstart, esempio di integrazione, tabella componenti, roadmap.
- `AGENTS.md` con i contratti dict completi di ogni template tag (per agenti AI e sviluppatori).
- `VISION.md` con posizionamento prodotto.
- `LICENSE` Apache 2.0.
- Configurazione `pyproject.toml` con `hatchling`, distribuzione wheel + sdist, classificatori, `dev` + `prod` extras.
- Pre-commit con `ruff`, `black`, `mypy`.
- Suite test: 87 test unitari pytest + 7 visual snapshot Playwright, tutti verdi.

### Modificato

- (release iniziale, niente da modificare)

### Rimosso

- (release iniziale, niente da rimuovere)

### Note tecniche

- `playwright==1.50.0` pinato per allinearlo ai browser pre-bundled nell'immagine `mcr.microsoft.com/playwright/python:v1.50.0-jammy`.
- Flag `--ignore-requires-python` nel servizio compose `playwright-tests` perche` l'immagine ha Python 3.10 mentre il pacchetto richiede `>=3.11` (vincolo per la pubblicazione, codice compatibile 3.10+).
- Host `web` in `DJANGO_ALLOWED_HOSTS` (dev) per permettere ai test visuali di puntare a `http://web:8000` via rete compose.

---

## [0.1.0-rc.1] — 2026-04-28

Release candidate. Sblocco baseline visual regression.

- M6 showcase living styleguide completo (riorganizzazione in 6 sezioni, sidebar TOC, pattern render-live + snippet, Playwright + 7 baseline PNG).

## [0.1.0-alpha.6] — 2026-04-27

- M5 feedback essenziale: `velora_alert`, `velora_label`, `velora_toast_messages`, componente JS `toast.js`.

## [0.1.0-alpha.5] — 2026-04-27

- M4 tabella e link essenziali: `velora_table`, `velora_pagination`, 4 link, `confirm.js`.

## [0.1.0-alpha.4] — 2026-04-27

- M3 form core: `velora_form_row` con 7 tipi base, `velora_search_box`, `velora_fields_separator`, `OnOffWidget`.

## [0.1.0-alpha.3] — 2026-04-26

- M2 layout core: `velora_header`, `velora_title_bar`, `base.html`, sidebar collassabile, settings di pacchetto.

## [0.1.0-alpha.2] — 2026-04-26

- M1 design system e pipeline build: tokens SCSS, reset, utilities, dart-sass + esbuild watcher, tag `{% velora_assets %}`.

## [0.1.0-alpha.1] — 2026-04-26

- M0 bootstrap: scaffolding `pyproject.toml` (hatchling), struttura `src/velora_ui`, app host `velora_project`, app `showcase`, settings minimi, Docker dev funzionante con `velora.local`.

## [0.0.1] — 2026-04-25

- Scaffolding iniziale del repository: `.gitignore`, `LICENSE`, `README.md` placeholder, `VISION.md`, piano operativo.
