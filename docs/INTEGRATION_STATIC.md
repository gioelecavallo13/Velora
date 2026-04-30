# Integrazione Velora UI senza Django (solo asset Web)

Gli asset CSS e JS ufficiali sono distribuiti **unicamente** come allegati delle **GitHub Releases** del repository. Non usare branch o commit come sorgente di produzione: fissa sempre un tag `vX.Y.Z` e scarica i file da quella release.

## Convenzione nomi file (`dist/` in CI)

Per la versione semver `X.Y.Z` (es. `0.8.0`), la build di release produce nella cartella `dist/` del runner (e allega alla Release):

| File | Contenuto |
|------|-----------|
| `velora-X.Y.Z.min.css` | Stylesheet minificato |
| `velora-X.Y.Z.min.css.map` | Source map CSS |
| `velora-X.Y.Z.min.js` | Bundle **core** ESM minificato (senza Chart.js) |
| `velora-X.Y.Z.min.js.map` | Source map JS core |
| `velora-X.Y.Z.full.min.js` | Bundle **full** ESM minificato (include Chart.js e `data-velora-component="chart-from-table"`) |
| `velora-X.Y.Z.full.min.js.map` | Source map JS full |

La cartella `dist/` alla radice del repository è in `.gitignore`: gli artifact vengono generati in CI al tag e pubblicati sulla Release, non versionati su `main`.

**Versione:** lo script `tools/build_web_dist.sh` legge `VELORA_VERSION` dall’ambiente se impostata, altrimenti `__version__` in `src/velora_ui/__init__.py`. In CI deve coincidere con il tag `vX.Y.Z`.

**Scelta del bundle:** usa il **core** (`min.js`) su pagine senza grafici da tabelle; usa il **full** (`full.min.js`) se impieghi `{% velora_chart_from_table %}` o markup con `chart-from-table`. Il CSS è unico (`min.css`) per entrambi.

Bundle **IIFE** non è incluso in questa release documentata; eventuali ampliamenti saranno descritti qui.

## URL di consumo (solo GitHub)

Schema obbligatorio per la documentazione ufficiale:

```text
https://github.com/{owner}/{repo}/releases/download/v{X.Y.Z}/velora-{X.Y.Z}.min.css
https://github.com/{owner}/{repo}/releases/download/v{X.Y.Z}/velora-{X.Y.Z}.min.js          # core
https://github.com/{owner}/{repo}/releases/download/v{X.Y.Z}/velora-{X.Y.Z}.full.min.js     # full (+ Chart)
```

Repository di riferimento: `https://github.com/gioelecavallo13/Velora.git` — sostituisci `{owner}`, `{repo}` e la versione con quelli effettivi.

### Esempio core (versione 0.8.0)

```html
<link
  rel="stylesheet"
  href="https://github.com/gioelecavallo13/Velora/releases/download/v0.8.0/velora-0.8.0.min.css"
/>
<script
  type="module"
  src="https://github.com/gioelecavallo13/Velora/releases/download/v0.8.0/velora-0.8.0.min.js"
></script>
```

### Esempio full (stessa release, con Chart.js)

```html
<link
  rel="stylesheet"
  href="https://github.com/gioelecavallo13/Velora/releases/download/v0.8.0/velora-0.8.0.min.css"
/>
<script
  type="module"
  src="https://github.com/gioelecavallo13/Velora/releases/download/v0.8.0/velora-0.8.0.full.min.js"
></script>
```

Il bundle è **ESM**: serve `type="module"`. È esposto anche `window.Velora` dopo il load.

## Progetti Django (`{% velora_assets %}`) e stessa GitHub Release

Per progetti che usano il pacchetto `velora-ui` è opzionale far puntare `{% velora_assets %}` agli **stessi file** allegati alla Release (un solo delivery layer, niente CDN terzi):

| Setting | Default | Effetto |
|--------|---------|--------|
| `VELORA_ASSETS_BASE_URL` | `""` | Se vuota, URL da `static()` come oggi. Se valorizzata, deve essere un prefisso HTTPS verso `…/releases/download/vX.Y.Z/` su **github.com**. |
| `VELORA_ASSETS_JS_FULL` | `True` | Con base Release: `velora-X.Y.Z.full.min.js` oppure, se `False`, bundle core `velora-X.Y.Z.min.js`. |

I nomi file usano `velora_ui.__version__`: la Release nel path (`vX.Y.Z`) e i file (`velora-X.Y.Z.*`) devono coincidere con la versione del wheel installato. Vedi [README.md](../README.md) (esempio settings).

## Repository privato e autenticazione

Le URL `releases/download/...` su repository **privati** richiedono una richiesta autenticata per scaricare i file (browser o `curl` senza token possono ricevere 404). Opzioni comuni:

- **Sviluppo:** scarica manualmente gli allegati dalla pagina della Release e servi i file dal tuo host o includili nel progetto.
- **CI / server:** usa un [GitHub token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) con scope `repo` (o fine-grained equivalente) nell’header `Authorization: Bearer <TOKEN>` o in query conforme alla documentazione GitHub.
- Non committare token o URL con secret incorporati.

## Pinning, integrità e aggiornamenti

- **Pinning:** usa sempre una versione esplicita nell’URL (`v0.8.0`), non `main` o `HEAD`.
- **Subresource Integrity (SRI):** dopo aver scaricato i file per una release, puoi aggiungere `integrity` e `crossorigin` su `<link>` e `<script>` secondo le best practice MDN. Rigenera l’hash quando cambi versione.
- **Aggiornamento:** consulta [CHANGELOG.md](../CHANGELOG.md), incrementa il tag nelle URL e verifica eventuali breaking change su classi o API JS.

## Snippet HTML (`docs/examples/`)

Il markup “web-first” è allineato ai partial Django in `src/velora_ui/templates/velora_ui/`. La **fonte operativa** per i componenti registrati è [`ui_registry/`](../ui_registry/) (vedi README): da lì si rigenerano i partial elencati in `registry.json`; la CI esegue `tools/sync_ui_registry.py --check`. I file in questa tabella restano esempi completi con URL Release; frammenti generati automaticamente sono in [`examples/_generated/`](examples/_generated/).

| Componente / tema | File snippet | Riferimento template |
|-------------------|-------------|----------------------|
| Layout app (header + sidebar + main), tema boot | [examples/minimal-app-shell.html](examples/minimal-app-shell.html) | `base.html`, `header/_header.html`, `sidebar/_sidebar.html` |
| Alert inline | [examples/alert.html](examples/alert.html) | `components/feedback/_alert.html` |
| Label / badge | [examples/label-badge.html](examples/label-badge.html) | `components/feedback/_label.html` |
| Label / badge (frammento sync) | [examples/_generated/label-badge-fragment.html](examples/_generated/label-badge-fragment.html) | stesso (generato da `ui_registry`) |
| Bottoni (`velora-btn`) e link header | [examples/buttons-and-links.html](examples/buttons-and-links.html) | `title_bar/_title_bar.html`, `header/_header.html` |
| Form row input testo | [examples/form-row-text.html](examples/form-row-text.html) | `form_row/text.html`, `_label`, `_help_error` |
| Toast (payload JSON + `Velora.toast`) | [examples/toast-programmatic.html](examples/toast-programmatic.html) | `velora_feedback.py` (`velora_toast_messages`), `js/.../toast.js` |
| Header menu dropdown | [examples/header-menu-static.html](examples/header-menu-static.html) | `header/_header.html` (`header-menu`) |
| Galleria Ionicons | [examples/ionicons-gallery-static.html](examples/ionicons-gallery-static.html) | `components/icons/_ionicons_gallery.html` |

Nei file sopra, CSS e JS usano **solo** URL `releases/download/...` come negli esempi precedenti; sostituisci owner, repo e versione con quelli della tua release pinnata.

### Ionicons (manifest e path)

Il bundle registra `data-velora-component="ionicons-gallery"`. Il componente legge **`data-manifest-url`** (JSON elenco icone) e **`data-icons-base`** (directory delle SVG). Quei file vivono nel pacchetto Django sotto gli static di Velora: in un sito solo-HTML devi **copiarli sul tuo server** (stessa versione del CSS/JS) e puntare gli attributi al path pubblico. Non sono parte del singolo file `.min.css` / `.min.js` allegato alla Release.

### Tema scuro

Come in `base.html`: prima del CSS, uno script legge `localStorage.getItem("velora-theme")` e, se vale `"dark"`, imposta `document.documentElement.setAttribute("data-velora-theme", "dark")`. La chiave prevista è `velora-theme`. Puoi impostarla da una tua UI prima del reload.

### Toast programmatico

Dopo il load del modulo è disponibile `window.Velora.toast` con metodi `success`, `error`, `warning`, `info` (messaggio, opzioni opzionali: `duration`, `dismissible`, `persistent`). In alternativa, per emulare `{% velora_toast_messages %}`, inserisci nel body uno o più tag

`<script type="application/json" data-velora-toast>...</script>`

con payload JSON `variant`, `message`, `tags` (vedi [velora_feedback.py](../src/velora_ui/templatetags/velora_feedback.py)).

## Markup e sicurezza (anti-XSS)

I componenti richiedono HTML con classi `velora-*` e attributi `data-velora-*` / `data-velora-component` come negli snippet e in [AGENTS.md](../AGENTS.md).

**Senza Django non c’è auto-escape server-side:** qualsiasi stringa proveniente da utente o da API va **sanitizzata o escapata** prima di finire in HTML (testo, `href`, attributi, JSON nei toast). Non concatenare HTML grezzo con input non attendibile. Per convenzioni complete (contesto template, messaggi, attributi sicuri) usa **AGENTS.md** come riferimento normativo per chi integra Velora in contesti statici o ibridi.

## Build locale degli stessi artifact

Con Node installato:

```bash
npm install
npm run build:web
```

Output in `dist/velora-<versione>.min.css`, `velora-<versione>.min.js` (core), `velora-<versione>.full.min.js` (full) e relative mappe. Utile per confrontare byte con la Release o per servire i file in ambiente chiuso.
