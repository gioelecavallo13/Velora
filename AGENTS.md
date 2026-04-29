# AGENTS.md — Contratti dei template tag Velora UI

Questo documento e` la **fonte di verita`** per i contratti dei template tag delle v0.1–v0.4: chiavi accettate dei dict in input, default, comportamento con valori mancanti o invalidi. Lo usano:

- gli **agenti AI** che generano codice che usa Velora (Cursor / Copilot / altri): qui trovano gli schema senza dover leggere i sorgenti
- gli **sviluppatori umani** che integrano Velora in un'app: qui trovano un riassunto pratico
- la **suite di test**: i test in `tests/` verificano che il comportamento descritto qui sia rispettato

Convenzioni:

- Tutti i tag fanno parte del package `velora_ui` e si caricano con `{% load velora_<modulo> %}`.
- Tutti i tag che ricevono dict ignorano silenziosamente le chiavi sconosciute (forward-compat) e applicano default sicuri ai valori mancanti.
- Tutte le stringhe in input vengono **HTML-escapate** prima del render (no XSS): se serve passare HTML grezzo va wrappato esplicitamente con `mark_safe` lato view.
- Le chiavi marcate **required** fanno fallire (silentemente o con `TemplateSyntaxError`, indicato caso per caso) la riga; il resto della pagina continua a renderizzare.

---

## Indice

- [`velora_assets`](#velora_assets)
- [`velora_layout` — header e title bar](#velora_layout)
- [`velora_forms` — form_row (v0.1 + v0.3), search_box, fields_separator, checkbox_tag (v0.3)](#velora_forms)
- [`velora_data` — table (v0.1 + v0.3 form-in-cell + selectable), pagination, select_all_table_rows (v0.3)](#velora_data)
- [`velora_links` — action/nav/delete/btn + v0.2: settings/toggle/copy/dropdown/dialog](#velora_links)
- [`velora_feedback` — alert, label, toast_messages](#velora_feedback)
- [`velora_navigation` — breadcrumb, submenu, progress (v0.2)](#velora_navigation)
- [`velora_overlays` — tooltip (v0.2)](#velora_overlays)
- [`velora_chart` — Chart.js da tabella HTML (v0.4, Fase 12)](#velora_chart)
- [Componenti aggiuntivi v0.4 (Fase 12) — logo, satisfaction, Ionicons, dark, i18n](#componenti-aggiuntivi-v04-fase-12)
  - [`velora_icon`](#velora_icon-library-velora_icons)
  - [`velora_ionicons_gallery`](#velora_ionicons_gallery-library-velora_icons)
- [Settings di pacchetto](#settings-di-pacchetto)
- [JS API pubblica `window.Velora`](#js-api-pubblica)

---

## `velora_assets`

```django
{% load velora_assets %}
{% velora_assets %}
```

Inietta nel `<head>` il `<link rel="stylesheet">` per `velora.css` e lo `<script type="module">` per `velora.js`. Gli asset compilati hanno cache busting via `staticfiles`.

Con `VELORA_ASSETS_BASE_URL` valorizzata (vedi sezione *Settings di pacchetto*), le URL puntano alla **stessa** GitHub Release (`velora-{version}.min.css` e JS core/full); il valore è validato (`https`, host `github.com`, path `releases/download/v…`).

Nessun parametro. Tag senza body.

---

## `velora_layout`

### `velora_header`

```django
{% load velora_layout %}
{% velora_header items=header_items %}
```

Renderizza l'header globale (brand + nav + user-menu).

**Parametri:**

| Param | Tipo | Default | Note |
|---|---|---|---|
| `items` | `list[dict]` | `context["velora_header_items"]` se presente, altrimenti `[]` | vedi schema item sotto |

**Tipi item supportati:** `link`, `user-menu` (v0.1) + `single-menu`, `multi-menu`, `apps-menu`, `notifications`, `logo` (v0.2).

Tipi sconosciuti → item scartato silenziosamente.

**Schema item — `link`** (v0.1):

```python
{
    "type": "link",
    "label": str,                   # required
    "url": str,                     # required
    "active": bool,                 # default False -> applica .is-active
    "extra_class": str,             # default ""
}
```

**Schema item — `user-menu`** (v0.1, allineato a destra):

```python
{
    "type": "user-menu",
    "label": str,                   # required (testo sul trigger, es. nome utente)
    "icon_slug": str,               # default "" — Ionicons accanto al label (es. person-sharp)
    "url": str,                     # required se `items` assente (link semplice)
    "items": [                      # opzionale: se non vuoto → dropdown come single-menu
        {"label": str, "url": str, "icon": str, "extra_class": str},
        ...
    ],
    "active": bool,                 # default False (solo modalità link)
    "extra_class": str,             # default ""
}
```

Con `items` valorizzato, `url` è opzionale (default `"#"`). Senza `items`, stessa firma di `link` (solo link al profilo).

**Schema item — `single-menu`** (v0.2):

```python
{
    "type": "single-menu",
    "label": str,                   # required (testo del trigger)
    "icon": str,                    # default "" (id icona, hook CSS per v0.4)
    "items": [                      # required, lista di link
        {"label": str, "url": str, "icon": str, "extra_class": str},
        ...
    ],
    "align": "left" | "right",      # default "left" (allineamento del pannello)
    "extra_class": str,             # default ""
}
```

Item con `items=[]` o `label=""` scartato. Sub-item senza `label` o `url` scartati.

**Schema item — `multi-menu`** (v0.2, mega-menu a colonne):

```python
{
    "type": "multi-menu",
    "label": str,                   # required
    "icon": str,                    # default ""
    "sections": [                   # required, lista di colonne
        {
            "label": str,           # default "" (titolo colonna; opzionale)
            "items": [              # required per colonna
                {"label": str, "url": str, "icon": str, "extra_class": str},
                ...
            ],
        },
        ...
    ],
    "align": "left" | "right",      # default "left"
    "extra_class": str,             # default ""
}
```

Colonne senza `items` validi vengono scartate.

**Schema item — `apps-menu`** (v0.2, griglia di app launcher):

```python
{
    "type": "apps-menu",
    "label": str,                   # default "App" (label screen-reader del trigger)
    "icon": str,                    # default "apps" (solo se `icon_slug` vuoto: classe .velora-icon--*)
    "icon_slug": str,               # default "" — se valorizzato (slug Ionicons), icona nel trigger al posto di `icon`
    "apps": [                       # required, lista
        {
            "label": str,           # required
            "url": str,              # required
            "icon": str,             # default ""
            "color": str,            # default "" (CSS color per la tile, es. "#4285f4")
        },
        ...
    ],
    "extra_class": str,             # default ""
}
```

Item con `apps=[]` scartato. App senza `label` o `url` scartate.

**Schema item — `notifications`** (v0.2, campanella + dropdown):

```python
{
    "type": "notifications",
    "label": str,                   # default "Notifiche"
    "icon": str,                    # default "bell" (solo se `icon_slug` vuoto)
    "icon_slug": str,               # default "" — slug Ionicons per l'icona del trigger (es. notifications-sharp)
    "unread_count": int,            # default 0; se >0 mostra badge rosso
    "items": [                      # default []
        {
            "title": str,           # required (notifica senza title scartata)
            "body": str,             # default ""
            "url": str,              # default "" (se vuoto la notifica non e` link)
            "timestamp": str,        # default ""  (es. "2 minuti fa")
            "unread": bool,          # default False -> applica .is-unread
        },
        ...
    ],
    "empty_label": str,             # default "Nessuna notifica"
    "footer_label": str,            # default "" (se non vuoto + footer_url -> link in fondo)
    "footer_url": str,              # default ""
    "extra_class": str,             # default ""
}
```

Sempre allineato a destra dell'header (forzato a `align="right"`).

**Schema item — `logo`** (v0.2, marchio aggiuntivo inline):

```python
{
    "type": "logo",
    "image_url": str,               # default ""
    "icon_slug": str,               # default "" — slug Ionicons (es. apps-sharp); se valorizzato con `image_url` vuoto viene mostrata l'icona SVG inline
    "label": str,                   # default ""
    "alt": str,                     # default = label (solo immagine `<img>`)
    "url": str,                     # default "/"
    "extra_class": str,             # default ""
}
```

Almeno uno fra `image_url`, `label` e `icon_slug` deve essere presente, altrimenti l'item viene scartato. Usato per affiancare al brand principale (`app_name` + `app_icon_url`) un secondo marchio (es. tenant).

**Comportamento generale:**

- App name e icona del brand principale: il context processor `velora_ui.context_processors.header_defaults` inietta `velora_header_app_name` e `velora_header_app_icon_url` letti dai settings `VELORA_HEADER_APP_NAME` / `VELORA_HEADER_APP_ICON_URL` (default: `"Velora UI"` e `None`).
- I tipi con pannello (`single-menu`, `multi-menu`, `apps-menu`, `notifications`, `user-menu` con `items`) sono auto-inizializzati dal componente JS `header-menu`: su viewport ampia con puntatore fine e hover, apertura al passaggio del mouse / focus sul wrapper; altrimenti toggle con click sul trigger; chevron del trigger nascosto solo in modalità hover. Click fuori chiude, ESC chiude, apertura mutuamente esclusiva.

### `velora_title_bar`

```django
{% velora_title_bar title="Clienti" actions=actions %}
```

**Parametri:**

| Param | Tipo | Default | Note |
|---|---|---|---|
| `title` | `str` | `""` | testo della barra titolo |
| `actions` | `list[dict]` | `None` | lista di azioni a destra |

**Schema action:**

```python
{
    "label": str,                            # default ""
    "url": str,                              # default ""
    "variant": "primary" | "secondary",     # default "secondary"
    "extra_class": str,                      # default ""
}
```

Le azioni rese non-dict vengono scartate.

---

## `velora_forms`

### `velora_form_row` — schema comune

```django
{% load velora_forms %}
{% velora_form_row type="text" name="email" label="Email aziendale" required=True %}
```

**Parametri comuni a tutti i tipi:**

| Param | Tipo | Default | Note |
|---|---|---|---|
| `type` | `str` | `"text"` | uno fra: `text`, `textarea`, `select`, `checkbox`, `radio`, `onoff`, `file` |
| `name` | `str` | — | **required**: lancia `TemplateSyntaxError` se vuoto |
| `label` | `str` | derivato da `name` (es. `nome_completo` → `"Nome completo"`) | |
| `value` | `Any` | `""` | valore corrente |
| `required` | `bool` | `False` | aggiunge attributo HTML `required` + asterisco nella label |
| `disabled` | `bool` | `False` | |
| `placeholder` | `str` | `""` | per text/textarea/search |
| `help_text` | `str` | `""` | riga sotto il control |
| `error` | `str` | `""` | se presente la riga riceve modificatore `--error` |
| `extra_class` | `str` | `""` | classi CSS extra sul wrapper |
| `autofocus` | `bool` | `False` | |
| `id` | `str` | `f"id_{name}"` | override id HTML |

Se `type` non e` riconosciuto → `TemplateSyntaxError` con elenco dei tipi disponibili.

### Parametri specifici per tipo

| Tipo | Param extra | Tipo | Default | Note |
|---|---|---|---|---|
| `text` | `input_type` | `str` | `"text"` | uno fra: `text`, `email`, `number`, `password`, `url`, `tel`, `search`. Tipo invalido → fallback `"text"` |
| `text` | `maxlength` | `int` | `None` | |
| `text` | `minlength` | `int` | `None` | |
| `text` | `pattern` | `str` | `""` | regex HTML |
| `textarea` | `rows` | `int` | `4` | |
| `select` | `choices` | `iterable` | `[]` | vedi schema choices sotto |
| `select` | `empty_label` | `str` | `""` | se non vuoto: aggiunge un `<option value="">empty_label</option>` in cima |
| `radio` | `choices` | `iterable` | `[]` | stesso schema di select |
| `checkbox` | (nessuno) | — | — | il valore booleano e` letto da `value` |
| `onoff` | `value_on` | `str` | `"1"` | valore submitted quando ON |
| `onoff` | `value_off` | `str` | `"0"` | valore submitted quando OFF |
| `file` | `accept` | `str` | `""` | es. `".pdf,image/*"` |
| `file` | `multiple` | `bool` | `False` | |

**Schema choices** (per `select` e `radio`):

```python
choices = [
    {"value": "admin", "label": "Amministratore", "disabled": False},  # forma esplicita
    ("user", "Utente"),                                                  # tupla (value, label)
    "guest",                                                             # stringa: value == label
]
```

Tutti normalizzati internamente a `[{value, label, disabled}]`.

### Parametri specifici per tipo (v0.3)

**Aggiunti in v0.3.0**: 9 nuovi field type. Tutti zero-deps (no librerie esterne). I parametri comuni (name/label/value/required/disabled/error/help_text/extra_class/autofocus/id) restano identici.

| Tipo | Param extra | Tipo | Default | Note |
|---|---|---|---|---|
| `datepicker` | `format` | `str` | `"YYYY-MM-DD"` | hint formato (validazione e` lato server) |
| `datepicker` | `min` / `max` | `str` | `""` | vincoli (stesso formato) |
| `datepicker` | `first_day` | `int` | `1` | 0=Domenica, 1=Lunedi |
| `datetimepicker` | `time_format` | `str` | `"HH:mm"` | |
| `datetimepicker` | `step_minutes` | `int` | `5` | granularita` minuti del select |
| `datetimepicker` | `format`, `min`, `max`, `first_day` | come datepicker | | |
| `multiselect` | `choices` | `iterable` | `[]` | stesso schema di `select` |
| `multiselect` | `value` | `list \| str` | `""` | pre-selezione (lista, CSV, valore singolo) |
| `autocomplete` | `options` | `iterable` | `[]` | `[{value,label}]`, tuple `(value,label)` o stringa |
| `autocomplete` | `min_chars` | `int` | `1` | caratteri minimi prima di filtrare |
| `remote_autocomplete` | `url` | `str` | — | **required**: lancia `TemplateSyntaxError` se vuoto |
| `remote_autocomplete` | `query_param` | `str` | `"q"` | nome del param GET |
| `remote_autocomplete` | `min_chars` | `int` | `2` | |
| `remote_autocomplete` | `debounce_ms` | `int` | `300` | |
| `remote_autocomplete` | `limit` | `int` | `10` | |
| `remote_autocomplete` | `value` | `str` | `""` | id selezione corrente (campo hidden) |
| `remote_autocomplete` | `value_label` | `str` | `""` | label da mostrare nel campo testo |
| `image_preview` | `accept` | `str` | `"image/*"` | |
| `image_preview` | `clearable` | `bool` | `True` | |
| `image_preview` | `max_size_kb` | `int` | `0` | hint client-side (0 = no check) |
| `image_preview` | `value` | `str` | `""` | URL preview iniziale |
| `image_preview` | `alt` | `str` | `""` | alt text dell'immagine |
| `rating_stars` | `max_value` | `int` | `5` | clamp 1..10 |
| `rating_stars` | `value` | `int` | `0` | stelle correnti (0 = nessuna) |
| `timer_fields` | `units` | `str \| list` | `"h,m,s"` | unita`: `y\|mo\|d\|h\|m\|s` |
| `timer_fields` | `value` | `int \| str` | `0` | durata corrente in **secondi** |
| `redactor` | `rows` | `int` | `8` | textarea fallback |
| `redactor` | `toolbar` | `str` | `"default"` | hint per il componente JS |

**Schema endpoint per `remote_autocomplete`**:

```json
[{"value": "1", "label": "Mario Rossi"}, {"value": "2", "label": "Luca Bianchi"}]
```

oppure:

```json
{"results": [{"value": "1", "label": "Mario Rossi"}, ...]}
```

Il client manda `?q=<term>` (configurabile via `query_param`), risponde max `limit` items. Header `X-Requested-With: XMLHttpRequest` automatico. `AbortController` cancella la richiesta in volo se l'utente continua a digitare.

**Comportamento generale (v0.3)**:

- Auto-init: tutti i field type avanzati si registrano via `data-velora-component="..."` e vengono inizializzati al boot e ad ogni mutation del DOM (compatibile HTMX/Turbo).
- Fallback no-JS: `multiselect` → `<select multiple>` nativo; `autocomplete` → input testo libero; `image_preview` → `<input type=file>` standard; `rating_stars` → 5 radio impilate.
- `redactor` e` un **stub minimal** (toolbar B/I/U/list/link via `execCommand`): per editor full-featured (Quill/TinyMCE) il consumer registri il proprio `data-velora-component="redactor"` _prima_ del `register()` di Velora, oppure sovrascriva la classe `.velora-redactor` via CSS.

### `velora_checkbox_tag` (v0.3)

```django
{% load velora_forms %}
{% velora_checkbox_tag name="agree" label="Accetto le condizioni" variant="success" %}
{% velora_checkbox_tag name="role" label="Admin" value="admin" radio=True variant="primary" %}
```

Checkbox/radio inline standalone (NON e` un `velora_form_row`: niente label sopra/help/error sotto, e` solo un control).

| Param | Tipo | Default | Note |
|---|---|---|---|
| `name` | `str` | `""` | required: tag emette stringa vuota se vuoto |
| `label` | `str` | `""` | testo accanto al control |
| `value` | `Any` | `"1"` | valore submitted |
| `checked` | `bool` | `False` | |
| `disabled` | `bool` | `False` | |
| `variant` | `"default" \| "primary" \| "info" \| "success" \| "danger"` | `"default"` | sconosciuto → fallback default |
| `align` | `"left" \| "right"` | `"left"` | sconosciuto → fallback left |
| `radio` | `bool` | `False` | se True usa `<input type=radio>` |
| `extra_class` | `str` | `""` | |
| `id` | `str` | derivato | default `id_<name>` per checkbox; per radio `id_<name>_<value>` (facilita group) |

### `velora_search_box`

```django
{% velora_search_box name="q" placeholder="Cerca cliente..." %}
```

| Param | Tipo | Default |
|---|---|---|
| `name` | `str` | `"q"` |
| `value` | `str` | `""` |
| `placeholder` | `str` | `"Cerca..."` |
| `action` | `str` | `""` (= submit alla URL corrente) |
| `method` | `str` | `"get"` |
| `label` | `str` | `""` (label nascosta visivamente) |
| `submit_label` | `str` | `"Cerca"` |
| `extra_class` | `str` | `""` |

### `velora_fields_separator`

```django
{% velora_fields_separator label="Dati di fatturazione" %}
```

| Param | Tipo | Default |
|---|---|---|
| `label` | `str` | `""` |
| `extra_class` | `str` | `""` |

Linea visiva con eventuale testo centrale.

---

## `velora_data`

### `velora_table`

```django
{% load velora_data %}
{% velora_table headers=headers rows=rows empty_message="Nessun cliente" %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `headers` | `iterable[str|dict]` | `[]` | schema sotto |
| `rows` | `iterable[list|dict]` | `[]` | schema sotto |
| `empty_message` | `str` | `"Nessun risultato"` | mostrato come singola cella `colspan` se `rows` vuoto |
| `extra_class` | `str` | `""` | sul `<table>` |
| `id` | `str` | `""` | id HTML opzionale |
| `selectable` | `bool` | `False` | (v0.3) aggiunge colonna iniziale con checkbox di riga + master |
| `row_id_key` | `str` | `"id"` | (v0.3) chiave per leggere l'id riga (solo se `selectable=True`) |

**Schema headers:**

```python
headers = [
    "Nome",                                              # stringa: solo label
    {"key": "email", "label": "Email"},                  # dict: necessario `key` se rows sono dict
    {"key": "actions", "label": "", "width": "120px",   # opzionali: width, align, extra_class
     "align": "right", "extra_class": ""},
]
```

**Schema rows:**

```python
# Forma 1: liste posizionali (in ordine degli headers)
rows = [
    ["Mario", "mario@x.it", "<a>...</a>"],
    ["Luca",  "luca@y.it",  "<a>...</a>"],
]

# Forma 2: dict pescati per `key` degli headers (le `key` mancanti = stringa vuota)
rows = [
    {"name": "Mario", "email": "mario@x.it"},
    {"name": "Luca",  "email": "luca@y.it"},
]
```

I valori delle celle non vengono escapati: la view e` libera di passare HTML pre-renderizzato (es. tag `velora_action_link`) wrappato con `mark_safe` o `format_html`.

**Schema cella editabile inline (v0.3 — form-in-cell)**:

Una cella puo` essere un dict con `form_in_cell` per attivare l'editing AJAX:

```python
{
    "value": "Mario",                 # fallback testo (no-JS o errore di schema)
    "form_in_cell": {
        "type": "text",               # text|number|select|checkbox|onoff (required)
        "name": "name",               # required (chiave per il backend)
        "value": "Mario",
        "url": "/api/users/1/",       # required: endpoint PATCH/POST
        "method": "patch",            # patch|post|put (default patch)
        "csrf": True,                 # default True (legge meta csrf-token)
        "auto_submit": True,          # default True (debounce 400ms su input testo)
        "row_id": 1,                  # opzionale: passato come `id` nella request
        "choices": [...],             # solo se type="select"
    },
}
```

Lato client: il componente JS `table-cell` legge `<meta name="csrf-token">` (preferito) o il cookie `csrftoken` (Django default), invia `FormData` via `fetch()` con header `X-Requested-With: XMLHttpRequest` e `X-CSRFToken: <token>`. Mostra status `Salvataggio... → ✓ → (errore)` accanto al control.

Schema invalido (es. `type` sconosciuto, `url` o `name` mancanti, `method` sconosciuto: fallback patch) → la cella renderizza solo `value` come testo statico (degrade gentile).

### `velora_pagination`

```django
{% velora_pagination page=page_obj base_url=request.path %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `page` | `Page \| dict \| None` | `None` | oggetto Page del Paginator Django o dict equivalente |
| `base_url` | `str` | `""` | URL base; se vuoto genera `?page=N` puri |
| `param` | `str` | `"page"` | nome del querystring |
| `extra_class` | `str` | `""` | sul `<nav>` wrapper |

**Schema dict equivalente al `Page` Django:**

```python
page = {
    "number": int,           # default 1
    "num_pages": int,        # default 1
    "has_previous": bool,    # default derivato da number > 1
    "has_next": bool,        # default derivato da number < num_pages
}
```

Render: link prev/next + finestra di al massimo 5 numeri attorno alla pagina corrente, gap `…` quando si salta. La pagina corrente e` un `<span aria-current="page">`, le altre `<a>`. Il querystring esistente di `base_url` viene preservato (override del solo `param`).

### `velora_select_all_table_rows` (v0.3)

```django
{% velora_select_all_table_rows
    target="#tab-clienti"
    url="/api/clienti/bulk/"
    actions=actions %}
{% velora_table id="tab-clienti" headers=h rows=r selectable=True %}
```

Toolbar bulk-actions agganciata a una tabella `selectable=True`.

| Param | Tipo | Default | Note |
|---|---|---|---|
| `target` | `str` | `""` | required (selettore CSS della tabella); se vuoto tag emette stringa vuota |
| `actions` | `list[dict]` | `None` | schema sotto |
| `url` | `str` | `""` | endpoint default per le azioni (override per action via `url` nel dict) |
| `name` | `str` | `"ids"` | nome del campo che contiene gli id selezionati (CSV) |
| `label` | `str` | `"Selezionati"` | prefisso del contatore (suffisso `(N)` aggiunto dal JS) |
| `extra_class` | `str` | `""` | |

**Schema action**:

```python
{
    "label": str,                                 # required
    "value": str,                                 # required (passato come `action` nel body)
    "url": str,                                   # default = url del tag
    "method": "post" | "patch" | "delete",        # default "post"; sconosciuto → "post"
    "variant": "primary" | "secondary" | "danger",# default "secondary"; sconosciuto → "secondary"
    "confirm": str,                               # default "" (se non vuoto: window.confirm prima del submit)
}
```

Item senza `label` o `value` scartato. Lato client: `select-all-table` sincronizza master + righe + contatore + abilita/disabilita azioni; submit FormData `action=<value>&<name>=id1,id2,...` con CSRF; emette CustomEvent `velora-bulk-done` (`{detail: {action, ids}}`) per consentire al consumer di aggiornare la pagina.

---

## `velora_links`

Tutti e 4 i tag accettano questo schema comune:

| Param | Tipo | Default | Note |
|---|---|---|---|
| `url` | `str` | `""` | se vuoto e non `disabled` → `href="#"` |
| `label` | `str` | `""` (su `velora_delete_link` default `"Elimina"`) | testo del link |
| `title` | `str` | `""` | tooltip native |
| `target` | `str` | `""` | se `"_blank"` aggiunge automaticamente `rel="noopener noreferrer"` |
| `rel` | `str` | `""` | override del rel automatico |
| `disabled` | `bool` | `False` | aggiunge `is-disabled`, `aria-disabled="true"`, `tabindex="-1"`, `href="#"` |
| `extra_class` | `str` | `""` | classi extra |

### `velora_action_link` — arancio

```django
{% velora_action_link url="/clients/42/edit/" label="Modifica" %}
```

CSS: `velora-link velora-link-action`. Per primary action di tabella o CTA della title bar.

### `velora_nav_link` — blu

```django
{% velora_nav_link url="/clients/42/" label="Vai al dettaglio" %}
```

CSS: `velora-link velora-link-nav`. Per link di navigazione interna sobri.

### `velora_delete_link` — rosso, con conferma

```django
{% velora_delete_link url="/clients/42/delete/" confirm_message="Eliminare 'Mario'?" %}
```

| Param extra | Tipo | Default |
|---|---|---|
| `confirm_message` | `str` | `"Confermi l'eliminazione?"` |
| `method` | `str` | `"post"` (alternativi: `"get"`, `"delete"`, ecc.) |

Renderizza un `<a>` con `data-velora-component="confirm"`. Il componente JS `confirm.js` intercetta il click, mostra `window.confirm(confirm_message)`, e se confermato crea al volo un form con CSRF token e fa submit con il `method` indicato. Fallback senza JS: link GET (la view deve gestire la conferma server-side).

### `velora_btn_link` — link stilizzato come bottone

```django
{% velora_btn_link url="/clients/new/" label="Nuovo cliente" variant="primary" %}
```

| Param extra | Tipo | Default | Note |
|---|---|---|---|
| `variant` | `"primary" \| "secondary"` | `"secondary"` | varianti success/danger arrivano in v0.2 |

CSS: `velora-btn velora-btn--<variant>`.

### `velora_settings_link` (v0.2) — verde

```django
{% velora_settings_link url="/cfg/" label="Impostazioni" %}
```

Stessa firma comune di `action_link/nav_link`. Default `label="Impostazioni"`. CSS: `velora-link velora-link-settings`.

### `velora_toggle_link` (v0.2) — mostra/nasconde

```django
{% velora_toggle_link target="#dettagli" label_show="Mostra" label_hide="Nascondi" initial_state="hidden" %}
<div id="dettagli" class="is-toggled-hidden">...</div>
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `target` | `str` | `""` | required (selettore CSS); se vuoto il tag non emette nulla |
| `label_show` | `str` | `"Mostra"` | label quando il target e` nascosto |
| `label_hide` | `str` | `"Nascondi"` | label quando il target e` visibile |
| `initial_state` | `"hidden" \| "shown"` | `"hidden"` | sconosciuto → fallback hidden |

JS `toggle.js` applica `is-toggled-hidden` (CSS `display: none !important`) sul target, sincronizza il testo del link e `aria-expanded`.

### `velora_copy_link` (v0.2) — copy-to-clipboard

```django
{% velora_copy_link value="velora-ui@0.2.0" label="Copia versione" %}
{% velora_copy_link target="#input-share" label="Copia link" %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `value` | `str` | `""` | testo statico (priorita` su target) |
| `target` | `str` | `""` | selettore CSS verso `<input>`/`<textarea>`/`<*>` |
| `label` | `str` | `"Copia"` | label normale |
| `label_copied` | `str` | `"Copiato"` | label temporanea post-copia (1.5s) |

Almeno uno fra `value` e `target` deve essere presente, altrimenti il tag non emette nulla. Usa `navigator.clipboard.writeText` con fallback `execCommand('copy')` per HTTP locali. Mostra toast Velora di esito (`success`/`error`).

### `velora_drop_down_link` (v0.2)

```django
{% velora_drop_down_link label="Altre azioni" items=[
    {"label": "Modifica", "url": "/edit/"},
    {"label": "Elimina",  "url": "/del/", "extra_class": "is-danger"},
] align="right" %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `label` | `str` | `""` | testo del trigger |
| `items` | `list[dict]` | `None` | required, sub-link `{label, url, icon?, extra_class?}` |
| `align` | `"left" \| "right"` | `"left"` | allineamento del pannello rispetto al trigger |
| `title` | `str` | `""` | tooltip native sul trigger |
| `extra_class` | `str` | `""` | classi extra sul wrapper |

Item senza `label` o `url` scartati. Lista vuota → tag emette stringa vuota. CSS trigger: `velora-link velora-link-dropdown`.

### `velora_drop_down_button` (v0.2)

```django
{% velora_drop_down_button label="Salva e..." items=actions variant="primary" %}
```

Stessa firma di `velora_drop_down_link` + `variant="primary"|"secondary"` (default `secondary`, fallback `secondary` su sconosciuto). CSS trigger: `velora-btn velora-btn--<variant>`.

### `velora_open_dialog_action_link` (v0.2)

```django
{# inline: dialog gia` nel DOM #}
{% velora_open_dialog_action_link label="Modifica" target="#dialog-edit" %}

{# remote: scarica fragment via AJAX #}
{% velora_open_dialog_action_link label="Anteprima" url="/preview/42/" size="lg" dialog_title="Anteprima" %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `label` | `str` | `""` | testo del link |
| `target` | `str` | `""` | selettore CSS al dialog inline |
| `url` | `str` | `""` | URL del fragment HTML |
| `size` | `"sm" \| "md" \| "lg"` | `"md"` | sconosciuto → fallback md |
| `dialog_title` | `str` | `""` | titolo dialog (solo modalita` remote) |
| `extra_class` | `str` | `""` | classi extra |

Almeno uno fra `target` e `url` deve essere presente, altrimenti il tag non emette nulla. Modalita` inline ha priorita` se entrambi presenti. Il fragment remoto e` recuperato con `X-Requested-With: XMLHttpRequest`.

---

## `velora_feedback`

### `velora_alert`

```django
{% load velora_feedback %}
{% velora_alert variant="success" message="Cliente salvato." dismissible=True %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `variant` | `str` | `"info"` | uno fra `success`, `error`, `warning`, `info`. Variant invalido → fallback `info` |
| `message` | `str` | `""` | testo principale |
| `title` | `str` | `""` | titolo opzionale (grassetto sopra) |
| `dismissible` | `bool` | `False` | aggiunge bottone X (rimuove il nodo dal DOM via JS inline) |
| `extra_class` | `str` | `""` | classi extra |

### `velora_label`

```django
{% velora_label variant="success" text="Attivo" %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `variant` | `str` | `"neutral"` | uno fra `success`, `error`, `warning`, `info`, `neutral`. Invalido → `neutral` |
| `text` | `str` | `""` | testo del badge |
| `extra_class` | `str` | `""` | |

### `velora_toast_messages`

```django
{% velora_toast_messages %}  {# in coda al body, usa request._messages #}
```

Bridge dal framework `django.contrib.messages` ai toast Velora. Per ogni messaggio in `messages.get_messages(request)` emette uno `<script type="application/json" data-velora-toast>` con payload:

```json
{"variant": "success", "message": "Salvato", "tags": "extra_tags string"}
```

Il componente JS `toast.js` legge questi script al `DOMContentLoaded` e li trasforma in toast.

**Mappatura level Django → variant Velora:**

| `messages.LEVEL` | variant |
|---|---|
| `DEBUG`, `INFO` | `info` |
| `SUCCESS` | `success` |
| `WARNING` | `warning` |
| `ERROR`, `CRITICAL` | `error` |

`extra_tags` di Django arrivano nel payload come `tags`: sono usabili dalla view per attivare opzioni custom (es. `messages.info(req, "...", extra_tags="persistent")` per disattivare l'auto-dismiss).

Lo `storage.used = True` viene impostato a fine lettura (Django pulisce i messaggi al request successivo).

---

## `velora_navigation`

Library v0.2 con breadcrumb, submenu e i tre progress bar.

### `velora_breadcrumb`

```django
{% load velora_navigation %}
{% velora_breadcrumb items=[
    {"label": "Home",    "url": "/"},
    {"label": "Clienti", "url": "/clients/"},
    {"label": "Mario Rossi"},
] %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `items` | `list[dict]` | `None` | items con `label` (required), `url` (opzionale: l'ultimo non ha link), `icon` (opzionale) |
| `separator` | `str` | `"›"` | separatore visivo |
| `extra_class` | `str` | `""` | |

Item senza `label` scartato. L'ultimo item ha `aria-current="page"` automaticamente.

### `velora_submenu`

```django
{% velora_submenu items=[
    {"label": "Generale", "url": "...", "active": True},
    {"label": "Tema",     "url": "..."},
] title="Impostazioni" %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `items` | `list[dict]` | `None` | `{label, url, icon?, active?, extra_class?}` |
| `title` | `str` | `""` | titolo opzionale |
| `extra_class` | `str` | `""` | |

Item senza `label` o `url` scartato. Lista vuota → tag non emette markup.

### `velora_progress_bar` (10.10 — classico)

```django
{% velora_progress_bar value=70 max=100 label="Caricamento" variant="success" %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `value` | `int \| float \| str` | `0` | castato safe |
| `max` | `int \| float \| str` | `100` | castato safe; se `<=0` la barra mostra 0% |
| `label` | `str` | `""` | etichetta sopra la barra |
| `variant` | `"default" \| "success" \| "warning" \| "danger" \| "info"` | `"default"` | sconosciuto → fallback default |
| `show_percent` | `bool` | `True` | mostra/nasconde % a destra del label |
| `extra_class` | `str` | `""` | |

`value` clampato in `[0, max]`. Render: `<div role="progressbar" aria-valuenow=...>` + barra `width: <pct>%`.

### `velora_condensed_progress_breadcrumb` (10.11 — wizard fasi)

```django
{% velora_condensed_progress_breadcrumb steps=[
    "Anagrafica", "Indirizzo", "Pagamento", "Conferma",
] current=2 %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `steps` | `list[str \| dict]` | `None` | stringhe (label) o dict `{label, url?}` |
| `current` | `int \| str` | `1` | 1-based; clamp a `[1, len(steps)]` |
| `extra_class` | `str` | `""` | |

Stati render: `is-done` (precedenti, verde + check), `is-current` (arancio + alone, `aria-current="step"`), `is-upcoming` (gray-100). Step `done` con `url` diventano link cliccabili.

### `velora_new_progress_bar` (10.12 — "X di Y")

```django
{% velora_new_progress_bar current=3 total=10 label="Upload file" %}
{% velora_new_progress_bar current=0 total=0 label="Indeterminato" %}  {# senza barra #}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `current` | `int \| str` | `0` | clamp `[0, total]` se `total>0` |
| `total` | `int \| str` | `0` | se `<=0` mostra contatore senza barra |
| `label` | `str` | `""` | |
| `variant` | stesso di `velora_progress_bar` | `"default"` | |
| `extra_class` | `str` | `""` | |

---

## `velora_overlays`

Library v0.2 per tooltip e helper di overlay (dialog viene da `velora_links` come trigger; il dialog vero in HTML usa le classi `.velora-dialog__*`).

### `velora_tooltip`

```django
{% load velora_overlays %}
<button {% velora_tooltip "Modifica cliente" placement="bottom" %}>X</button>
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `text` | `str` | `""` | required; se vuoto il tag emette stringa vuota |
| `placement` | `"top" \| "bottom" \| "left" \| "right"` | `"top"` | sconosciuto → top |
| `delay` | `int` | `200` | ms; valori `<0` clampati a 0 |

Il tag emette **solo** la stringa di attributi `data-velora-component="tooltip" data-tooltip-text="..." data-tooltip-placement="..." data-tooltip-delay="..."`: niente wrapper, da iniettare in elementi esistenti. Il componente JS `tooltip.js` mostra/nasconde un balloon globale singolo riusato fra tutti i trigger.

---

## `velora_chart`

Library **v0.4 (Fase 12.1)**: grafici [Chart.js](https://www.chartjs.org/) costruiti a partire da una tabella HTML nel DOM. Il bundle `velora.js` include Chart.js (aumenta sensibilmente la dimensione del file ~da 56 KB a ~480 KB in v0.4 — accettabile per admin panel; in futuro si puo` valutare code-splitting).

Python: il modulo `velora_ui.chartutils` espone `VALID_CHART_TYPES` e `normalize_chart_type()`.

### `velora_chart_from_table`

```django
{% load velora_chart %}
<table id="demo-sales">
  <thead>
    <tr><th></th><th>Q1</th><th>Q2</th><th>Q3</th></tr>
  </thead>
  <tbody>
    <tr><td>Italia</td><td>10</td><td>20</td><td>15</td></tr>
    <tr><td>Germania</td><td>5</td><td>8</td><td>12</td></tr>
  </tbody>
</table>
{% velora_chart_from_table table_selector="#demo-sales" chart_type="line" canvas_id="chart-sales" %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `table_selector` | `str` | `""` | required; selettore CSS della tabella; se vuoto il tag non emette nulla |
| `chart_type` | `"line" \| "bar" \| "pie"` | `"line"` | sconosciuto → `line` |
| `canvas_id` | `str` | `"velora-chart-canvas"` | id del `<canvas>` (**usare id unici** se piu` grafici in pagina) |
| `height` | `int \| str` | `280` | altezza del box in px (clamp minimo 80) |
| `extra_class` | `str` | `""` | classi sul wrapper `.velora-chart` |

**Convenzione dati — `line` e `bar`:** prima riga in `<thead>`: primo `<th>` opzionale, i successivi sono le etichette asse X. Ogni `<tr>` in `<tbody>`: primo `<td>` = nome serie, i successivi = valori numerici (supporta virgola come decimale, spazi e simboli euro ignorati solo parzialmente — preferire numeri plain).

**Convenzione dati — `pie`:** ogni riga del `<tbody>` ha due celle: etichetta fetta, valore numerico.

Richiede `{% velora_assets %}` (o equivalente) cosi` Chart.js e` caricato. Il componente `chart-from-table` distrugge un'istanza Chart precedente sullo stesso wrapper prima di ricreare il grafico (re-init sicuro).

---

## Componenti aggiuntivi v0.4 (Fase 12)

### `velora_logo` (library `velora_layout`)

Marchio standalone (non l’intero header). Almeno uno fra `image_url` e `label` (dopo strip) deve essere valorizzato; altrimenti il tag non emette markup.

```django
{% load velora_layout %}
{% velora_logo image_url="/static/acme.svg" label="Acme" url="/" size="md" alt="" extra_class="" %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `image_url` | `str` | `""` | |
| `label` | `str` | `""` | |
| `url` | `str` | `"/"` | |
| `size` | `"sm" \| "md" \| "lg"` | `"md"` | invalido → `md` |
| `alt` | `str` | `""` | default → `label` |
| `extra_class` | `str` | `""` | |

### `velora_satisfaction_bar` (library `velora_feedback`)

Barra a segmenti orizzontali (stile KPI / soddisfazione).

```django
{% load velora_feedback %}
{% velora_satisfaction_bar value=3 max_value=5 label="NPS" variant="default" aria_label="" extra_class="" %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `value` | `int`-like | `0` | clamp `>= 0`, riempimento max `max_value` |
| `max_value` | `int`-like | `5` | se `<=0` fallback a `5` |
| `label` | `str` | `""` | |
| `variant` | `"default" \| "success" \| "danger"` | `"default"` | sconosciuto → `default` |
| `aria_label` | `str` | `""` | default → `label` |

### `velora_icon` (library `velora_icons`)

Icona **Ionicons** come SVG **inline** (consigliato) con `currentColor`, oppure come `<img lazy>` per casi isolati. Asset in `static/velora_ui/icons/ionicons/` dopo `npm run sync:icons`.

```django
{% load velora_icons %}
{% velora_icon "home-outline" %}
{% velora_icon "settings-outline" size="lg" extra_class="my-toolbar-icon" %}
{% velora_icon "warning-outline" alt="Avviso" size="sm" %}
{% velora_icon "logo-ionitron" as_img=True width=24 height=24 alt="" %}
```

| Param | Tipo | Default | Note |
|---|---|---|---|
| `name` | `str` | `""` | slug file senza `.svg`; vuoto o non valido → stringa vuota |
| `extra_class` | `str` | `""` | classi sul wrapper `.velora-icon` (o su `<img>` se `as_img`) |
| `alt` | `str` | `""` | se non vuoto: `role="img"` + `aria-label`; altrimenti `aria-hidden="true"` |
| `width` | `int` | `22` | ignorato se `size` è uno fra sm/md/lg/xl |
| `height` | `int` | stesso di `width` | |
| `size` | `str` | `""` | `sm`→18px, `md`→22px, `lg`→28px, `xl`→36px |
| `as_img` | bool | `False` | `True` → `<img>` lazy (gallerie dense o email); niente tema via `color` |

**CSS:** wrapper `.velora-icon`; variabile opzionale `--velora-icon-color` per forzare il colore ereditato dall’SVG. Regole in `scss/_icon.scss`.

### `velora_ionicons_gallery` (library `velora_icons`)

Galleria a griglia con titolo, campo ricerca, hint (default: invito a scrivere «tutte»). Ogni scheda mostra l’icona, l’etichetta **`ion-` + slug** (stile naming simile al Teamartist content-showcase) e un snippet `{% velora_icon 'slug' %}`. Click sulla scheda copia lo **slug** negli appunti.

Con **`search_url`** valorizzato (URL di una view JSON che risponda come l’endpoint showcase `GET /api/ionicons/?q=&limit=`), il componente JS interroga il server a ogni ricerca (debounce ~200 ms): ricerca AJAX. Senza `search_url`, carica `ionicons-manifest.json` e filtra in client (fallback).

**Showcase:** `showcase.views.ionicons_search` + `path("api/ionicons/", ...)`; nel context della pagina passare `search_url` risolto con `reverse`.

| Param | Tipo | Default | Note |
|---|---|---|---|
| `search_input_id` | `str` | `"velora-ionicons-search"` | id dell’`<input type="search">` |
| `search_placeholder` | `str` | _(tradotto)_ | |
| `search_label` | `str` | _(tradotto)_ | per `<label>` accessibile |
| `search_url` | `str` | `""` | se non vuoto → ricerche `fetch` verso questa URL (querystring `q`, `limit`) |
| `section_title` | `str` | `Ionicons` | titolo sopra al campo ricerca |
| `hint` | `str` | _(testo «tutte»)_ | sottotesto esplicativo |

Risposta JSON attesa da `search_url`: `{ "icons": [...], "total_icons": N, "matched": M, "returned": R, "truncated": bool, "is_initial": bool }`.

Il componente JS registrato e` `ionicons-gallery`.

### Tema dark (CSS)

Attivazione: `data-velora-theme="dark"` su `<html>`. Il template `velora_ui/base.html` esegue uno script inline in `<head>` che legge `localStorage["velora-theme"]` per evitare il flash del tema sbagliato. Il componente JS `theme-toggle` ( `data-velora-component="theme-toggle"`) commuta tema e scrive `localStorage`. Stili in `scss/_theme-dark.scss`.

### i18n (progetto host + showcase)

Il progetto host deve abilitare `LocaleMiddleware`, `LANGUAGES`, `LOCALE_PATHS` e la view `django.views.i18n.set_language` (nell’esempio `velora_project`: `path("i18n/setlang/", ...)`). Cataloghi `.po/.mo` in `showcase/locale/` (showcase) e opzionalmente sotto `src/velora_ui/locale/` per stringhe del pacchetto marcate con `gettext_lazy`. Dopo aver modificato i `.po`, eseguire `django-admin compilemessages`.

---

## Settings di pacchetto

In `settings.py` di un progetto host:

| Setting | Tipo | Default | Effetto |
|---|---|---|---|
| `VELORA_HEADER_APP_NAME` | `str` | `"Velora UI"` | Brand mostrato nell'header |
| `VELORA_HEADER_APP_ICON_URL` | `str \| None` | `None` | URL dell'icona; se `None` non viene reso il `<img>` |
| `VELORA_ASSETS_BASE_URL` | `str` | `""` | Se non vuota, prefisso HTTPS `…github.com/…/releases/download/vX.Y.Z/` per `{% velora_assets %}`; altrimenti `static()`. Vietati host diversi da GitHub (nessun CDN terzo). |
| `VELORA_ASSETS_JS_FULL` | `bool` | `True` | Con base Release: carica `velora-X.Y.Z.full.min.js`; se `False`, bundle core `velora-X.Y.Z.min.js`. |

Per essere applicati serve aggiungere il context processor:

```python
TEMPLATES = [{
    # ...
    "OPTIONS": {"context_processors": [
        # ...
        "velora_ui.context_processors.header_defaults",
    ]},
}]
```

---

## JS API pubblica

L'unica API JS pubblica e` su `window.Velora` (ESM modules sotto al cofano):

```js
// Toast: shortcut per ogni variante
Velora.toast.success("Salvato")
Velora.toast.error("Operazione fallita")
Velora.toast.warning("Verifica i dati")
Velora.toast.info("Sessione in scadenza")

// Toast: API esplicita
Velora.toast.show({
  variant: "info",     // default "info"; uno fra success/error/warning/info
  message: "...",      // testo
  duration: 5000,      // ms; default 5000
  dismissible: true,   // default true
  persistent: false,   // se true, niente auto-dismiss (override duration)
})

// Pulisci tutti i toast attivi
Velora.toast.dismissAll()

// Registrazione di un componente custom (auto-init via MutationObserver)
Velora.register({
  name: "my-component",
  init(el) { /* ... */ },
})
```

Tutti i componenti Velora si auto-inizializzano cercando elementi con `data-velora-component="<name>"` nel DOM al boot e ad ogni mutazione del DOM (drop-in compatibile con HTMX/Turbo).

---

## Compatibilita`

Le firme documentate qui valgono per `v0.1.x`, `v0.2.x`, `v0.3.x`. Tutte le aggiunte di `v0.2.0` e `v0.3.0` sono state **additive** (nuovi tipi/parametri opzionali con default sicuri, full backward compatibility con v0.1). Le modifiche **breaking** saranno annunciate nel `CHANGELOG.md` e raggruppate in una `v0.x.0` con bump minor (semver pre-1.0).

**Lock-in API in v0.3**: avendo saltato il gate strategico di feedback su v0.2 (richiesto: 1-2 settimane di uso reale) gli schema dei nuovi field type avanzati (datepicker, multiselect, autocomplete, ecc.) e del form-in-cell sono **provvisori**. Eventuali aggiustamenti raccolti dall'uso reale saranno raggruppati in una `v0.4.0` con sezione "Breaking" dedicata.
