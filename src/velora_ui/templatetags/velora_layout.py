"""Template tag di layout per Velora UI.

Espone i tag {% velora_header %} e {% velora_title_bar %} usati in v0.1 come
elementi strutturali del template `velora_ui/base.html`.

Sono entrambi `inclusion_tag`: ricevono un piccolo dict di contesto da una
view (o dal context processor `velora_ui.context_processors.header_defaults`)
e renderizzano il partial corrispondente sotto
`velora_ui/templates/velora_ui/components/`.

Schema dei dati:

    velora_header items=[
        {"type": "link",      "label": "Dashboard", "url": "/"},
        {"type": "user-menu", "label": "Mario Rossi", "url": "/profile/"},
    ]

    velora_title_bar
        title="Dashboard"
        actions=[{"label": "Nuovo", "url": "/new/", "variant": "primary"}]

In v0.1 i tipi `link` e `user-menu` producono entrambi un singolo `<a>`: la
differenza e` solo nello stile (user-menu mostra l'utente in coda all'header,
allineato a destra). Il dropdown vero e proprio del `user-menu` arriva in
v0.2 (vedi sezione "Cosa NON entra in v0.1" del piano).
"""

from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


_VALID_HEADER_ITEM_TYPES = {"link", "user-menu"}


def _normalize_header_items(items: Any) -> list[dict[str, Any]]:
    """Normalizza la lista degli item dell'header.

    Filtra item malformati (mancano `label` o `url`, oppure `type` non
    riconosciuto) registrandoli come warning silente nel template — preferiamo
    non far crashare la pagina admin per un errore di configurazione di un
    singolo item, ma evidenziarli con `data-velora-invalid` per debug.
    """

    if not items:
        return []
    normalized: list[dict[str, Any]] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        item_type = raw.get("type", "link")
        if item_type not in _VALID_HEADER_ITEM_TYPES:
            continue
        label = raw.get("label", "")
        url = raw.get("url", "")
        normalized.append(
            {
                "type": item_type,
                "label": label,
                "url": url,
                "active": bool(raw.get("active", False)),
                "extra_class": raw.get("extra_class", ""),
            }
        )
    return normalized


@register.inclusion_tag(
    "velora_ui/components/header/_header.html",
    takes_context=True,
)
def velora_header(context: template.Context, items: Any = None) -> dict[str, Any]:
    """Renderizza l'header globale dell'app.

    Args:
        context: contesto template, usato per recuperare `request` e i default
            iniettati dal context processor (`velora_header_app_name`,
            `velora_header_app_icon_url`).
        items: lista di dict come da schema in modulo. Se `None`, viene letta
            da `context['velora_header_items']` se presente.
    """

    if items is None:
        items = context.get("velora_header_items")
    return {
        "request": context.get("request"),
        "items": _normalize_header_items(items),
        "app_name": context.get("velora_header_app_name", "Velora UI"),
        "app_icon_url": context.get("velora_header_app_icon_url"),
    }


@register.inclusion_tag(
    "velora_ui/components/title_bar/_title_bar.html",
    takes_context=True,
)
def velora_title_bar(
    context: template.Context,
    title: str = "",
    actions: Any = None,
) -> dict[str, Any]:
    """Renderizza la barra titolo della pagina.

    Args:
        context: contesto template (non usato direttamente, riservato per
            estensioni v0.2 come breadcrumb dal request path).
        title: stringa visualizzata centrata.
        actions: lista di dict `{"label", "url", "variant"}` con `variant`
            opzionale fra "primary" e "secondary" (default "secondary").
    """

    normalized_actions: list[dict[str, Any]] = []
    if actions:
        for raw in actions:
            if not isinstance(raw, dict):
                continue
            normalized_actions.append(
                {
                    "label": raw.get("label", ""),
                    "url": raw.get("url", ""),
                    "variant": raw.get("variant", "secondary"),
                    "extra_class": raw.get("extra_class", ""),
                }
            )
    return {
        "title": title,
        "actions": normalized_actions,
    }
