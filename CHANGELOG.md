# Changelog

Tutte le modifiche significative a Velora UI sono documentate in questo file.

Il formato si ispira a [Keep a Changelog](https://keepachangelog.com/) e il versionamento segue [Semantic Versioning](https://semver.org/) — pre-1.0 ogni `0.x.0` puo` introdurre breaking change documentati qui.

## [0.4.0] — 2026-04-29

Quarta release: **Chart.js** (già in 12.1), **set Ionicons** con galleria ricercabile nello showcase, **`velora_logo`** e **`velora_satisfaction_bar`**, **tema scuro** (`data-velora-theme` + `localStorage`), **i18n** (catalogo inglese parallelo all’italiano per showcase + stringhe traducibili nei tag icone).

### Aggiunto

- `velora_logo` in `velora_layout`: marchio standalone (immagine e/o testo); output vuoto se entrambi assenti.
- `velora_satisfaction_bar` in `velora_feedback`: segmenti orizzontali con varianti `default` / `success` / `danger`.
- `velora_ionicons_gallery` in `velora_icons`: shell template + JS `ionicons-gallery`; sync asset con `npm run sync:icons` (`tools/sync_ionicons.sh`).
- SCSS: `_theme-dark.scss`, `_satisfaction.scss`, `_logo.scss`, `_ionicons.scss` inclusi in `velora.scss`.
- JS: `theme_toggle.js` registrato come `theme-toggle`.
- Showcase: sezioni `#chart`, `#ionicons`, `#theme-brand`; lingua IT/EN via `set_language` e catalogo `showcase/locale/en/LC_MESSAGES/django.{po,mo}`.
- Progetto host: `LocaleMiddleware`, `LANGUAGES`, `LOCALE_PATHS`, URL `i18n/setlang/`, context processor `django.template.context_processors.i18n`.
- Test: `test_layout` (logo), `test_feedback` (satisfaction), `test_icons`, `test_i18n_urls`; snapshot Playwright estesi con tre ancore (`chart`, `ionicons`, `theme-brand`) — **aggiornare le baseline** con `pytest tests/visual --update-snapshots` nel container Playwright.

### Modificato

- `LANGUAGE_CODE` normalizzato a `it` (era `it-it`).
- `showcase/views.py`: etichette sidebar e title actions avvolte in `gettext_lazy`.

### Corretto

- `ionicons_gallery.js`: stringa conteggio risultati (template literal rotto) ripristinata.

## [0.3.0] — 2026-04-29

Terza release: **form avanzati & tabelle interattive**. Aggiunti 9 nuovi `field_type` per `velora_form_row` (datepicker, datetimepicker, multiselect, autocomplete locale + remoto, image_preview, rating_stars, timer_fields, redactor), estensione di `velora_table` con form-in-cell AJAX e selezione multi-riga, nuovo tag `velora_select_all_table_rows` con bulk-actions, nuovo tag standalone `velora_checkbox_tag` con 5 varianti colore. Tutti i nuovi componenti JS sono **zero-dipendenze runtime** (no Flatpickr, no Select2, no Choices.js, no Quill).

### Aggiunto

#### Form row avanzati (`velora_forms.velora_form_row`)
- `type="datepicker"`: input testo + calendario popup custom (zero deps). Supporta `format` (default `YYYY-MM-DD`), `min`/`max`, `first_day` (0=Dom, 1=Lun, default 1), navigazione mensile, oggi/pulisci/conferma.
- `type="datetimepicker"`: estensione del datepicker con select ore + minuti, `time_format` (default `HH:mm`), `step_minutes` (default 5), conferma esplicita.
- `type="multiselect"`: `<select multiple>` nativo (fallback no-JS) trasformato dal componente JS in UI con chip rimuovibili + dropdown delle opzioni; pre-selezione tramite `value` (lista, CSV o singolo valore).
- `type="autocomplete"` (locale): opzioni inline come JSON in `<script type="application/json">`; filter in memoria al keyup, navigation via Arrow Up/Down, conferma con Enter o click.
- `type="remote_autocomplete"` (AJAX): `url` required, `query_param` (default `q`), `min_chars` (default 2), `debounce_ms` (default 300), `limit` (default 10). Ritorna lista JSON `[{value,label}]` o `{results:[...]}`. Doppio campo: visibile (label) + hidden (value submit-ready). `AbortController` per cancellare richieste in volo.
- `type="image_preview"`: `<input type=file accept="image/*">` con preview thumbnail; `value` URL come immagine iniziale, `clearable=True` (default) aggiunge bottone rimuovi, `max_size_kb` per limite client-side con toast error in caso di sforamento.
- `type="rating_stars"`: 5 stelle (configurabile via `max_value`, clamp 1..10). Implementato come radio button nativi (CSS `:checked + general sibling`) + JS opzionale per hover preview. Submit invia il valore numerico `1..max`.
- `type="timer_fields"`: input multipli per durata composita (anni/mesi/giorni/ore/minuti/secondi). `units` come stringa CSV o lista (es. `"h,m,s"` default). Hidden field `name` con il totale in secondi sincronizzato in tempo reale.
- `type="redactor"`: textarea + toolbar minimale (B, I, U, list, link, removeFormat) via `document.execCommand` per esperienza decente out-of-the-box senza dipendenze; consumer puo` registrare proprio componente per editor full-featured (Quill/TinyMCE/ProseMirror).

#### Tabelle interattive (`velora_data`)
- `velora_table`: due nuovi parametri opzionali:
  - `selectable=True` aggiunge una colonna iniziale con checkbox di riga + master in `<thead>`. Le righe devono essere dict per esporre `row_id_key` (default `"id"`) come identificativo passato al backend.
  - Cella **form-in-cell**: il valore di una cella puo` essere `{value, form_in_cell: {type, name, value, url, method, csrf, auto_submit, choices?, row_id?}}`. Tipi supportati: `text`, `number`, `select`, `checkbox`, `onoff` (toggle visivo). Il componente JS `table-cell` ascolta change/blur/Enter, costruisce FormData con CSRF token (letto da `<meta name="csrf-token">` o cookie `csrftoken`), invia `fetch()` al `url` con metodo `method` (default PATCH).
- `velora_select_all_table_rows`: toolbar bulk-actions agganciata a una tabella `selectable=True` via `target="#id"`. `actions=[{label, value, url?, method?, variant?, confirm?}]` con varianti `primary`/`secondary`/`danger`; il JS `select-all-table` sincronizza il master, mostra il contatore `(N)`, abilita le azioni solo se ci sono righe selezionate, gestisce il submit AJAX e la conferma `window.confirm` quando richiesta. Emette `velora-bulk-done` (CustomEvent) per consentire al consumer di reagire (refresh, redirect, ecc.).

#### Checkbox tag (`velora_forms`)
- `velora_checkbox_tag`: checkbox/radio standalone (non form_row) per uso inline in tabelle, toolbar, list-item. 5 varianti colore: `default` (arancio), `primary` (blu), `info` (azzurro), `success` (verde), `danger` (rosso). Modalita` `radio=True` per radio group. `align="left|right"`, stato `disabled` con styling sobrio. Nome vuoto -> tag emette stringa vuota.

### Modificato

- `velora_table` mantiene 100% backward compatible: i due nuovi parametri (`selectable`, `row_id_key`) sono opzionali e con default sicuri. Le celle stringa/HTML continuano a funzionare come in v0.1; il riconoscimento del form-in-cell e` puramente _opt-in_ (richiede struttura dict con chiave `form_in_cell`).
- `velora.scss`: aggiunti 3 nuovi partial (`form-row-v03`, `table-v03`, `checkbox`).
- `velora.js`: registrati 9 nuovi componenti (`datepicker`, `multiselect`, `autocomplete`, `image-preview`, `rating`, `timer`, `redactor`, `table-cell`, `select-all-table`). Bundle: 56 KB (era 16 KB; +40 KB per i 9 nuovi componenti).

### Test

- `tests/test_forms_v03.py`: 37 nuovi test per i 9 nuovi field type + checkbox tag (rendering, normalizzazione input, fallback su valori invalidi, casting stringa->numero/lista, attributi data-* corretti).
- `tests/test_data_v03.py`: 17 nuovi test per form-in-cell + selectable + select_all (schema, scarto silenzioso di item malformati, default sicuri).
- `tests/visual/test_showcase.py`: aggiunte 3 sezioni alla parametrizzazione (`form-advanced`, `tables-advanced`, `checkbox`); 13 snapshot Playwright (era 10).
- **Suite full v0.3: 222/222 verdi** (209 unit + 13 visual). Era 165/165 in v0.2 (+57 nuovi test).

### Showcase

- Nuova sezione `#form-advanced`: demo "snippet + render live" di tutti i 9 field type avanzati (datepicker, datetimepicker, multiselect con preselezione, autocomplete locale, remote_autocomplete, image_preview con max-size, rating con valore predefinito, timer_fields con valore composito, redactor con HTML iniziale).
- Nuova sezione `#tables-advanced`: tabella editabile inline con 3 utenti (`text`, `select`, `onoff` form-in-cell) + bulk-actions toolbar con archivia/elimina (con confirm).
- Nuova sezione `#checkbox`: dimostrazione di tutte e 5 le varianti colore + radio group + stato disabled + align right.
- Sidebar TOC estesa con 3 nuove voci (`Form avanzati`, `Tabelle interattive`, `Checkbox`).

### Note tecniche

- **Strategia "zero deps"**: scelta consapevole di NON usare Flatpickr/Choices.js/Select2/Quill nonostante alcuni casi avrebbero beneficiato (es. il datepicker custom non ha keyboard navigation completa). Pattern: in v0.x manteniamo zero deps; un eventuale `velora-ui-extras` separato in v1.0+ potra` impacchettare integrazioni opzionali con librerie pesanti. Il `redactor` e` lo stub piu` minimal: il consumer puo` sostituirlo registrando un proprio componente `data-velora-component="redactor"` _prima_ del `register()` di Velora.
- **Form-in-cell e CSRF**: il componente legge il token da `<meta name="csrf-token">` (preferito) o dal cookie `csrftoken` (Django default). Per il primo metodo bisogna iniettare il meta nel base template del progetto host: `<meta name="csrf-token" content="{{ csrf_token }}">`. Senza CSRF la richiesta partira` senza header e Django rispondera` 403 (gestito a livello di consumer; Velora non genera errori).
- **Bundle JS cresciuto a 56 KB**: il datepicker (~6 KB), il dialog (~3 KB), e i nuovi componenti pesano. Per progetti che usano solo un sottoinsieme, in v0.4 sara` valutato lo split in chunks separati con import dinamico.
- **API lock-in**: avendo saltato il gate strategico di feedback su v0.2 (richiesto: 1-2 settimane), gli schema dei nuovi field type rimangono **provvisori**. Eventuali breaking change saranno raccolti in una `v0.4.0` con nota dedicata.

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
