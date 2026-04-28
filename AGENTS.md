# AGENTS.md — Contratti dei template tag Velora UI

Questo documento e` la **fonte di verita`** per i contratti dei template tag della v0.1: chiavi accettate dei dict in input, default, comportamento con valori mancanti o invalidi. Lo usano:

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
- [`velora_forms` — form_row, search_box, fields_separator](#velora_forms)
- [`velora_data` — table, pagination](#velora_data)
- [`velora_links` — action/nav/delete/btn link](#velora_links)
- [`velora_feedback` — alert, label, toast_messages](#velora_feedback)
- [Settings di pacchetto](#settings-di-pacchetto)
- [JS API pubblica `window.Velora`](#js-api-pubblica)

---

## `velora_assets`

```django
{% load velora_assets %}
{% velora_assets %}
```

Inietta nel `<head>` il `<link rel="stylesheet">` per `velora.css` e lo `<script type="module">` per `velora.js`. Gli asset compilati hanno cache busting via `staticfiles`.

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

**Schema item:**

```python
{
    "type": "link" | "user-menu",   # required, fallback "link"
    "label": str,                   # required (item senza label viene scartato)
    "url": str,                     # required (item senza url viene scartato)
    "active": bool,                 # default False -> applica .is-active
    "extra_class": str,             # default "" -> appeso al class dell'<a>
}
```

**Comportamento:**

- Tipi diversi da `link`/`user-menu` → item scartato silenziosamente (in v0.2 si aggiungono `single-menu`, `multi-menu`, `apps-menu`, `notifications`).
- `user-menu` produce lo stesso `<a>` di `link` ma e` allineato a destra; il dropdown vero arriva in v0.2.
- App name e icona: il context processor `velora_ui.context_processors.header_defaults` inietta `velora_header_app_name` e `velora_header_app_icon_url` letti dai settings `VELORA_HEADER_APP_NAME` / `VELORA_HEADER_APP_ICON_URL` (default: `"Velora UI"` e `None`).

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

## Settings di pacchetto

In `settings.py` di un progetto host:

| Setting | Tipo | Default | Effetto |
|---|---|---|---|
| `VELORA_HEADER_APP_NAME` | `str` | `"Velora UI"` | Brand mostrato nell'header |
| `VELORA_HEADER_APP_ICON_URL` | `str \| None` | `None` | URL dell'icona; se `None` non viene reso il `<img>` |

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

Le firme documentate qui valgono per `v0.1.x`. Le aggiunte di `v0.2.0` saranno **additive** (nuovi tipi/parametri opzionali con default sicuri). Le modifiche **breaking** saranno annunciate nel `CHANGELOG.md` e raggruppate in una `v0.x.0` con bump minor (semver pre-1.0).
