"""Template tag per i form di Velora UI (M3 — Fase 5 del piano).

Espone:
  - {% velora_form_row type="..." name="..." ... %}  -> riga di form
  - {% velora_search_box name="q" placeholder="..." %}-> input ricerca
  - {% velora_fields_separator label="oppure" %}     -> separatore visivo

`velora_form_row` fa dispatch sul template specifico di tipo (vedi
``TYPE_TEMPLATE_MAP``). I tipi supportati in v0.1 sono i 7 elencati nel piano:

    text | textarea | select | checkbox | radio | onoff | file

I tipi avanzati (datepicker, datetimepicker, multiselect, redactor,
autocomplete, remote_autocomplete, image_preview, rating_stars,
timer_fields) sono rimandati a v0.2/v0.3 — vedi sezione "Cosa NON entra in
v0.1" del piano.

Schema parametri comune a tutti i tipi:

    name        (str, required)  -> attributo `name` dell'input
    label       (str)            -> testo della <label>; default capitalizza name
    value       (Any)            -> valore corrente
    required    (bool)           -> required HTML + asterisco nella label
    disabled    (bool)
    placeholder (str)            -> per text/textarea/select
    help_text   (str)            -> riga sotto il control
    error       (str)            -> messaggio errore; se presente la riga
                                    riceve il modificatore `--error`
    extra_class (str)            -> classi extra sul wrapper della riga
    autofocus   (bool)
    id          (str)            -> override id; default `id_<name>`

Parametri specifici dei tipi sono documentati nel docstring di
``velora_form_row``.
"""

from __future__ import annotations

import json
from typing import Any

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


TYPE_TEMPLATE_MAP: dict[str, str] = {
    # v0.1
    "text": "velora_ui/components/form_row/text.html",
    "textarea": "velora_ui/components/form_row/textarea.html",
    "select": "velora_ui/components/form_row/select.html",
    "checkbox": "velora_ui/components/form_row/checkbox.html",
    "radio": "velora_ui/components/form_row/radio.html",
    "onoff": "velora_ui/components/form_row/onoff.html",
    "file": "velora_ui/components/form_row/file.html",
    # v0.3 (Fase 11)
    "datepicker": "velora_ui/components/form_row/datepicker.html",
    "datetimepicker": "velora_ui/components/form_row/datetimepicker.html",
    "multiselect": "velora_ui/components/form_row/multiselect.html",
    "autocomplete": "velora_ui/components/form_row/autocomplete.html",
    "remote_autocomplete": "velora_ui/components/form_row/remote_autocomplete.html",
    "image_preview": "velora_ui/components/form_row/image_preview.html",
    "rating_stars": "velora_ui/components/form_row/rating_stars.html",
    "timer_fields": "velora_ui/components/form_row/timer_fields.html",
    "redactor": "velora_ui/components/form_row/redactor.html",
}


_VALID_TEXT_INPUT_TYPES = {
    "text",
    "email",
    "number",
    "password",
    "url",
    "tel",
    "search",
}


def _default_label(name: str) -> str:
    """Genera un'etichetta leggibile da un name in snake_case/kebab-case."""

    if not name:
        return ""
    cleaned = name.replace("_", " ").replace("-", " ").strip()
    return cleaned[:1].upper() + cleaned[1:]


def _build_common_context(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Estrae e normalizza i parametri comuni a tutti i form_row."""

    name = kwargs.get("name", "")
    if not name:
        raise template.TemplateSyntaxError(
            "{% velora_form_row %}: 'name' e` obbligatorio"
        )
    return {
        "name": name,
        "id": kwargs.get("id") or f"id_{name}",
        "label": kwargs.get("label", _default_label(name)),
        "value": kwargs.get("value", ""),
        "required": bool(kwargs.get("required", False)),
        "disabled": bool(kwargs.get("disabled", False)),
        "placeholder": kwargs.get("placeholder", ""),
        "help_text": kwargs.get("help_text", ""),
        "error": kwargs.get("error", ""),
        "extra_class": kwargs.get("extra_class", ""),
        "autofocus": bool(kwargs.get("autofocus", False)),
    }


def _normalize_choices(raw: Any) -> list[dict[str, Any]]:
    """Normalizza le `choices` per select/radio in [{value, label, selected}]."""

    if not raw:
        return []
    normalized: list[dict[str, Any]] = []
    for entry in raw:
        if isinstance(entry, dict):
            normalized.append(
                {
                    "value": entry.get("value", ""),
                    "label": entry.get("label", entry.get("value", "")),
                    "disabled": bool(entry.get("disabled", False)),
                }
            )
        elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
            normalized.append(
                {"value": entry[0], "label": entry[1], "disabled": False}
            )
        else:
            normalized.append({"value": entry, "label": entry, "disabled": False})
    return normalized


# ---------------------------------------------------------------------------
# Helper v0.3 (Fase 11) — field type avanzati
# ---------------------------------------------------------------------------


def _coerce_int(value: Any, default: int) -> int:
    """Cast safe int; default su valori invalidi."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_str_list(value: Any) -> list[str]:
    """Accetta lista, tupla o stringa CSV."""
    if value is None or value == "":
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value if v not in (None, "")]
    if isinstance(value, str):
        return [chunk.strip() for chunk in value.split(",") if chunk.strip()]
    return [str(value)]


def _normalize_multiselect_value(value: Any) -> set[str]:
    """Normalizza il `value` di un multiselect a set di stringhe."""
    if value is None or value == "":
        return set()
    if isinstance(value, (list, tuple, set, frozenset)):
        return {str(v) for v in value}
    if isinstance(value, str):
        return {chunk.strip() for chunk in value.split(",") if chunk.strip()}
    return {str(value)}


def _normalize_autocomplete_options(raw: Any) -> list[dict[str, str]]:
    """Normalizza le opzioni di autocomplete in [{value, label}]."""
    if not raw:
        return []
    normalized: list[dict[str, str]] = []
    for entry in raw:
        if isinstance(entry, dict):
            label = str(entry.get("label", entry.get("value", "")))
            value = str(entry.get("value", label))
            if not label:
                continue
            normalized.append({"value": value, "label": label})
        elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
            normalized.append({"value": str(entry[0]), "label": str(entry[1])})
        else:
            s = str(entry)
            if s:
                normalized.append({"value": s, "label": s})
    return normalized


_RATING_STAR_LABELS = {
    1: "Pessimo",
    2: "Mediocre",
    3: "Sufficiente",
    4: "Buono",
    5: "Ottimo",
}


def _build_rating_stars(max_value: int, current: int) -> list[dict[str, Any]]:
    """Costruisce la lista di stelle per `rating_stars`. Ordine: dal valore
    massimo al minimo (cosi` il pattern CSS ":checked ~ *" colora a sinistra
    della selezionata).
    """
    if max_value < 1:
        max_value = 5
    if max_value > 10:
        max_value = 10
    stars: list[dict[str, Any]] = []
    for v in range(max_value, 0, -1):
        stars.append(
            {
                "value": v,
                "label": _RATING_STAR_LABELS.get(v, str(v)),
                "selected": v == current,
            }
        )
    return stars


# Definizioni canoniche delle unita` di durata supportate da `timer_fields`.
# Mappa key -> (suffisso visivo, secondi per unita`, max accettato per il
# sub-input). `max=None` = nessun cap.
_TIMER_UNITS: dict[str, tuple[str, int, int | None]] = {
    "y": ("anni", 365 * 24 * 3600, None),
    "mo": ("mesi", 30 * 24 * 3600, 11),
    "d": ("giorni", 24 * 3600, 29),
    "h": ("ore", 3600, 23),
    "m": ("min", 60, 59),
    "s": ("sec", 1, 59),
}


def _build_timer_units(
    units_keys: list[str], total_seconds: int
) -> list[dict[str, Any]]:
    """Distribuisce `total_seconds` nelle unita` indicate (in ordine
    decrescente di grandezza) usando divisione intera con resto.
    Le unita` sconosciute vengono ignorate silenziosamente.
    """
    valid = [k for k in units_keys if k in _TIMER_UNITS]
    if not valid:
        valid = ["h", "m", "s"]
    # Ordina per "secondi per unita`" decrescente (anni -> secondi)
    valid_sorted = sorted(valid, key=lambda k: -_TIMER_UNITS[k][1])

    remaining = max(int(total_seconds), 0)
    out: list[dict[str, Any]] = []
    for key in valid_sorted:
        suffix, secs_per_unit, unit_max = _TIMER_UNITS[key]
        unit_value = remaining // secs_per_unit
        remaining -= unit_value * secs_per_unit
        out.append(
            {
                "key": key,
                "suffix": suffix,
                "seconds": secs_per_unit,
                "value": unit_value,
                "max": unit_max,
            }
        )
    return out


@register.simple_tag
def velora_form_row(**kwargs: Any) -> SafeString:
    """Renderizza una riga di form, dispatch sul tipo.

    Parametri specifici per tipo:

      type="text"
        input_type (str): uno fra text|email|number|password|url|tel|search
                         (default "text"); validato e fallback a "text" se invalido
        maxlength  (int): max length HTML
        minlength  (int)
        pattern    (str): regex per validazione HTML

      type="textarea"
        rows       (int): righe visualizzate (default 4)

      type="select"
        choices    (iterable): elenco di {value,label} oppure tuple (value,label)
        empty_label(str): se valorizzato aggiunge una option vuota in cima

      type="checkbox"
        (nessun parametro extra; il valore booleano e` letto da `value`)

      type="radio"
        choices    (iterable)

      type="onoff"
        (nessun parametro extra; toggle on/off, valore booleano)

      type="file"
        accept     (str): es. ".pdf,image/*"
        multiple   (bool)

      type="datepicker"  (v0.3)
        format     (str): default "YYYY-MM-DD"
        min/max    (str): vincoli formato `format`
        first_day  (int): 0=Domenica, 1=Lunedi (default 1)

      type="datetimepicker"  (v0.3)
        format/min/max/first_day come datepicker
        time_format  (str): default "HH:mm"
        step_minutes (int): incremento minuti (default 5)

      type="multiselect"  (v0.3)
        choices (iterable): stesso schema di select
        value (str|list): pre-selezione (CSV o lista)

      type="autocomplete"  (v0.3)
        options    (iterable): [{value,label}] o tuple/string locali
        min_chars  (int): default 1

      type="remote_autocomplete"  (v0.3)
        url          (str, required): endpoint che ritorna lista JSON
        query_param  (str): default "q"
        min_chars    (int): default 2
        debounce_ms  (int): default 300
        limit        (int): default 10
        value        (str): id della selezione corrente
        value_label  (str): label da mostrare nel campo testo

      type="image_preview"  (v0.3)
        accept        (str): default "image/*"
        clearable     (bool): default True
        max_size_kb   (int): hint client-side (0 = no check)
        value         (str): URL preview iniziale
        alt           (str): testo alternativo

      type="rating_stars"  (v0.3)
        max_value (int): default 5 (clamp 1..10)
        value     (int): stelle correnti (0 = nessuna)

      type="timer_fields"  (v0.3)
        units (str|list): unita` da renderizzare in CSV;
            keys: y(anni)|mo(mesi)|d(giorni)|h(ore)|m(min)|s(sec).
            Default "h,m,s".
        value (int|str): durata corrente in secondi

      type="redactor"  (v0.3)
        rows    (int): default 8 (textarea fallback)
        toolbar (str): hint per il componente JS (default "default")
    """

    field_type = kwargs.get("type", "text")
    template_name = TYPE_TEMPLATE_MAP.get(field_type)
    if template_name is None:
        raise template.TemplateSyntaxError(
            f"{{% velora_form_row %}}: type {field_type!r} non supportato in v0.1. "
            f"Tipi disponibili: {sorted(TYPE_TEMPLATE_MAP)}"
        )

    ctx = _build_common_context(kwargs)
    ctx["field_type"] = field_type

    if field_type == "text":
        input_type = kwargs.get("input_type", "text")
        if input_type not in _VALID_TEXT_INPUT_TYPES:
            input_type = "text"
        ctx["input_type"] = input_type
        ctx["maxlength"] = kwargs.get("maxlength")
        ctx["minlength"] = kwargs.get("minlength")
        ctx["pattern"] = kwargs.get("pattern", "")
    elif field_type == "textarea":
        ctx["rows"] = int(kwargs.get("rows", 4))
    elif field_type in ("select", "radio"):
        ctx["choices"] = _normalize_choices(kwargs.get("choices"))
        ctx["empty_label"] = kwargs.get("empty_label", "")
        # Per il selected/checked confronto come stringhe per uniformita`
        ctx["value_str"] = "" if ctx["value"] is None else str(ctx["value"])
    elif field_type == "checkbox":
        ctx["checked"] = bool(kwargs.get("value", False))
    elif field_type == "onoff":
        ctx["checked"] = bool(kwargs.get("value", False))
        ctx["value_on"] = kwargs.get("value_on", "1")
        ctx["value_off"] = kwargs.get("value_off", "0")
    elif field_type == "file":
        ctx["accept"] = kwargs.get("accept", "")
        ctx["multiple"] = bool(kwargs.get("multiple", False))
    elif field_type == "datepicker":
        ctx["format"] = kwargs.get("format", "YYYY-MM-DD")
        ctx["min"] = kwargs.get("min", "")
        ctx["max"] = kwargs.get("max", "")
        ctx["first_day"] = _coerce_int(kwargs.get("first_day", 1), 1)
    elif field_type == "datetimepicker":
        ctx["format"] = kwargs.get("format", "YYYY-MM-DD")
        ctx["time_format"] = kwargs.get("time_format", "HH:mm")
        ctx["step_minutes"] = _coerce_int(kwargs.get("step_minutes", 5), 5)
        ctx["min"] = kwargs.get("min", "")
        ctx["max"] = kwargs.get("max", "")
        ctx["first_day"] = _coerce_int(kwargs.get("first_day", 1), 1)
        ctx["datetime_placeholder"] = f"{ctx['format']} {ctx['time_format']}"
    elif field_type == "multiselect":
        selected_values = _normalize_multiselect_value(ctx["value"])
        choices_norm = _normalize_choices(kwargs.get("choices"))
        for choice in choices_norm:
            choice["selected"] = str(choice.get("value", "")) in selected_values
        ctx["choices"] = choices_norm
    elif field_type == "autocomplete":
        opts = _normalize_autocomplete_options(kwargs.get("options"))
        ctx["options_json"] = json.dumps(opts, ensure_ascii=False)
        ctx["min_chars"] = _coerce_int(kwargs.get("min_chars", 1), 1)
    elif field_type == "remote_autocomplete":
        url = str(kwargs.get("url", "")).strip()
        if not url:
            raise template.TemplateSyntaxError(
                "{% velora_form_row %} type='remote_autocomplete': "
                "'url' e` obbligatorio"
            )
        ctx["url"] = url
        ctx["query_param"] = kwargs.get("query_param", "q")
        ctx["min_chars"] = _coerce_int(kwargs.get("min_chars", 2), 2)
        ctx["debounce_ms"] = _coerce_int(kwargs.get("debounce_ms", 300), 300)
        ctx["limit"] = _coerce_int(kwargs.get("limit", 10), 10)
        ctx["value_label"] = kwargs.get("value_label", "")
    elif field_type == "image_preview":
        accept = kwargs.get("accept", "image/*")
        if not accept:
            accept = "image/*"
        ctx["accept"] = accept
        ctx["alt"] = kwargs.get("alt", "")
        ctx["clearable"] = bool(kwargs.get("clearable", True))
        ctx["max_size_kb"] = _coerce_int(kwargs.get("max_size_kb", 0), 0)
    elif field_type == "rating_stars":
        max_value = _coerce_int(kwargs.get("max_value", 5), 5)
        current = _coerce_int(ctx["value"], 0)
        ctx["stars"] = _build_rating_stars(max_value, current)
        ctx["max_value"] = max_value
    elif field_type == "timer_fields":
        units_keys = _coerce_str_list(kwargs.get("units", "h,m,s"))
        total_seconds = _coerce_int(ctx["value"], 0)
        if total_seconds < 0:
            total_seconds = 0
        ctx["units"] = _build_timer_units(units_keys, total_seconds)
        ctx["units_csv"] = ",".join(u["key"] for u in ctx["units"])
        ctx["value_seconds"] = total_seconds
    elif field_type == "redactor":
        ctx["rows"] = _coerce_int(kwargs.get("rows", 8), 8)
        ctx["toolbar"] = kwargs.get("toolbar", "default")

    return mark_safe(render_to_string(template_name, ctx))


@register.inclusion_tag("velora_ui/components/form_row/_search_box.html")
def velora_search_box(
    name: str = "q",
    value: str = "",
    placeholder: str = "Cerca...",
    action: str = "",
    method: str = "get",
    label: str = "",
    submit_label: str = "Cerca",
    extra_class: str = "",
) -> dict[str, Any]:
    """Renderizza una search box: <form><input type=search><button submit></form>.

    `action` vuoto = submit alla URL corrente (comportamento HTML standard).
    """

    return {
        "name": name,
        "value": value,
        "placeholder": placeholder,
        "action": action,
        "method": method.lower() if method else "get",
        "label": label,
        "submit_label": submit_label,
        "extra_class": extra_class,
    }


@register.inclusion_tag("velora_ui/components/form_row/_fields_separator.html")
def velora_fields_separator(
    label: str = "",
    extra_class: str = "",
) -> dict[str, Any]:
    """Separatore visivo: linea con eventuale testo centrale (es. "oppure")."""

    return {
        "label": label,
        "extra_class": extra_class,
    }


# ---------------------------------------------------------------------------
# velora_checkbox_tag (v0.3)
# ---------------------------------------------------------------------------


_CHECKBOX_VARIANTS = {"default", "primary", "info", "success", "danger"}


@register.inclusion_tag("velora_ui/components/form_row/_checkbox_tag.html")
def velora_checkbox_tag(
    name: str = "",
    label: str = "",
    value: Any = "1",
    checked: bool = False,
    disabled: bool = False,
    variant: str = "default",
    align: str = "left",
    radio: bool = False,
    extra_class: str = "",
    id: str = "",
) -> dict[str, Any]:
    """Render di una checkbox/radio standalone (non dentro un form_row).

    Varianti colore: default (arancio), primary (blu), info (azzurro),
    success (verde), danger (rosso). Sconosciuto -> default.

    Args:
        name: required (se vuoto il tag emette stringa vuota)
        label: testo accanto al control
        value: valore submitted
        checked: stato iniziale
        disabled: disattiva l'input
        variant: variante colore
        align: 'left' (default) o 'right' (control a destra del label)
        radio: se True usa <input type=radio> invece di checkbox
        extra_class: classi extra sul wrapper
        id: id HTML override (default `id_<name>_<value>` per facilitare
            radio group; per checkbox `id_<name>` se non override)
    """
    if not name:
        # Inclusion_tag deve sempre restituire un dict; il template usa
        # `{% if name %}` per non emettere markup quando name e` vuoto.
        return {
            "name": "",
            "label": "",
            "value": "",
            "checked": False,
            "disabled": False,
            "variant": "default",
            "align": "left",
            "input_type": "checkbox",
            "extra_class": "",
            "id": "",
        }
    if variant not in _CHECKBOX_VARIANTS:
        variant = "default"
    if align not in ("left", "right"):
        align = "left"
    if not id:
        if radio:
            slug = str(value).replace(" ", "_") if value not in (None, "") else "x"
            id = f"id_{name}_{slug}"
        else:
            id = f"id_{name}"
    return {
        "name": name,
        "label": label,
        "value": value,
        "checked": bool(checked),
        "disabled": bool(disabled),
        "variant": variant,
        "align": align,
        "input_type": "radio" if radio else "checkbox",
        "extra_class": extra_class,
        "id": id,
    }
