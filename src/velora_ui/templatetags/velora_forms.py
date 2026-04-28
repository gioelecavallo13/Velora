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

from typing import Any

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


TYPE_TEMPLATE_MAP: dict[str, str] = {
    "text": "velora_ui/components/form_row/text.html",
    "textarea": "velora_ui/components/form_row/textarea.html",
    "select": "velora_ui/components/form_row/select.html",
    "checkbox": "velora_ui/components/form_row/checkbox.html",
    "radio": "velora_ui/components/form_row/radio.html",
    "onoff": "velora_ui/components/form_row/onoff.html",
    "file": "velora_ui/components/form_row/file.html",
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
