"""Template tag di layout per Velora UI.

Classi CSS principali (markup in templates/velora_ui/components/):
  - Header: .velora-header e sottoclassi .velora-header__*
  - Title bar: .velora-title-bar, .velora-title-bar__text, .velora-title-bar__meta,
    .velora-title-bar__title, .velora-title-bar__actions, .velora-btn
  - Logo: .velora-logo, .velora-logo__img, .velora-logo__text
"""

from __future__ import annotations

from typing import Any

from django import template

from velora_ui.templatetags.velora_icons import _normalize_slug

register = template.Library()


_VALID_HEADER_ITEM_TYPES = {
    "link",
    "user-menu",
    "single-menu",
    "multi-menu",
    "apps-menu",
    "notifications",
    "logo",
}

_VALID_PANEL_ALIGNMENTS = {"left", "right"}


def _coerce_subitems(raw_items: Any) -> list[dict[str, Any]]:
    """Normalizza la lista di sotto-link {label, url, extra_class}."""

    if not raw_items:
        return []
    out: list[dict[str, Any]] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        label = raw.get("label", "")
        url = raw.get("url", "")
        if not label or not url:
            continue
        out.append(
            {
                "label": label,
                "url": url,
                "icon": raw.get("icon", ""),
                "extra_class": raw.get("extra_class", ""),
            }
        )
    return out


def _coerce_sections(raw_sections: Any) -> list[dict[str, Any]]:
    """Normalizza le sezioni del multi-menu: ognuna {label?, items:[...]}.

    Le sezioni senza alcun item dopo il filtro vengono scartate, cosi` non
    si mostrano colonne vuote.
    """

    if not raw_sections:
        return []
    out: list[dict[str, Any]] = []
    for raw in raw_sections:
        if not isinstance(raw, dict):
            continue
        items = _coerce_subitems(raw.get("items"))
        if not items:
            continue
        out.append(
            {
                "label": raw.get("label", ""),
                "items": items,
            }
        )
    return out


def _coerce_apps(raw_apps: Any) -> list[dict[str, Any]]:
    """Normalizza la griglia di app: {label, url, icon?, color?}."""

    if not raw_apps:
        return []
    out: list[dict[str, Any]] = []
    for raw in raw_apps:
        if not isinstance(raw, dict):
            continue
        label = raw.get("label", "")
        url = raw.get("url", "")
        if not label or not url:
            continue
        out.append(
            {
                "label": label,
                "url": url,
                "icon": raw.get("icon", ""),
                "color": raw.get("color", ""),
            }
        )
    return out


def _coerce_notifications(raw_items: Any) -> list[dict[str, Any]]:
    """Normalizza le notifiche: {title, body?, url?, timestamp?, unread?}."""

    if not raw_items:
        return []
    out: list[dict[str, Any]] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        title = raw.get("title", "")
        if not title:
            continue
        out.append(
            {
                "title": title,
                "body": raw.get("body", ""),
                "url": raw.get("url", ""),
                "timestamp": raw.get("timestamp", ""),
                "unread": bool(raw.get("unread", False)),
            }
        )
    return out


def _coerce_unread_count(raw: Any) -> int:
    """Normalizza il contatore notifiche a `int >= 0`. Fallback 0."""

    try:
        value = int(raw)
    except (TypeError, ValueError):
        return 0
    return max(0, value)


def _normalize_panel_align(raw: Any) -> str:
    align = raw if isinstance(raw, str) else ""
    return align if align in _VALID_PANEL_ALIGNMENTS else "left"


def _normalize_header_items(items: Any) -> list[dict[str, Any]]:
    """Normalizza la lista degli item dell'header.

    Filtra item malformati (mancano `label` o `url` quando richiesti, oppure
    `type` non riconosciuto, oppure pannello vuoto). Item validi vengono
    arricchiti con default sicuri per permettere al template di non avere
    branching su chiavi mancanti.
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

        common = {
            "type": item_type,
            "label": raw.get("label", ""),
            "extra_class": raw.get("extra_class", ""),
        }

        if item_type == "link":
            label = common["label"]
            url = raw.get("url", "")
            if not label or not url:
                continue
            normalized.append(
                {
                    **common,
                    "url": url,
                    "active": bool(raw.get("active", False)),
                }
            )

        elif item_type == "user-menu":
            label = common["label"]
            url = raw.get("url", "")
            icon_slug = _normalize_slug(str(raw.get("icon_slug", "")))
            menu_items = _coerce_subitems(raw.get("items"))
            if menu_items:
                if not label:
                    continue
                normalized.append(
                    {
                        **common,
                        "url": url or "#",
                        "icon_slug": icon_slug,
                        "menu_items": menu_items,
                        "active": bool(raw.get("active", False)),
                    }
                )
            else:
                if not label or not url:
                    continue
                normalized.append(
                    {
                        **common,
                        "url": url,
                        "icon_slug": icon_slug,
                        "active": bool(raw.get("active", False)),
                    }
                )

        elif item_type == "single-menu":
            sub_items = _coerce_subitems(raw.get("items"))
            if not common["label"] or not sub_items:
                continue
            normalized.append(
                {
                    **common,
                    "icon": raw.get("icon", ""),
                    "items": sub_items,
                    "align": _normalize_panel_align(raw.get("align")),
                }
            )

        elif item_type == "multi-menu":
            sections = _coerce_sections(raw.get("sections"))
            if not common["label"] or not sections:
                continue
            normalized.append(
                {
                    **common,
                    "icon": raw.get("icon", ""),
                    "sections": sections,
                    "align": _normalize_panel_align(raw.get("align")),
                }
            )

        elif item_type == "apps-menu":
            apps = _coerce_apps(raw.get("apps"))
            if not apps:
                continue
            icon_slug = _normalize_slug(str(raw.get("icon_slug", "")))
            normalized.append(
                {
                    **common,
                    "label": common["label"] or "App",
                    "icon": raw.get("icon", "apps"),
                    "icon_slug": icon_slug,
                    "apps": apps,
                }
            )

        elif item_type == "notifications":
            entries = _coerce_notifications(raw.get("items"))
            unread = _coerce_unread_count(raw.get("unread_count", 0))
            footer_label = raw.get("footer_label", "")
            footer_url = raw.get("footer_url", "")
            icon_slug = _normalize_slug(str(raw.get("icon_slug", "")))
            normalized.append(
                {
                    **common,
                    "label": common["label"] or "Notifiche",
                    "icon": raw.get("icon", "bell"),
                    "icon_slug": icon_slug,
                    "items": entries,
                    "unread_count": unread,
                    "empty_label": raw.get("empty_label", "Nessuna notifica"),
                    "footer_label": footer_label,
                    "footer_url": footer_url,
                }
            )

        elif item_type == "logo":
            image_url = raw.get("image_url", "")
            icon_slug = _normalize_slug(str(raw.get("icon_slug", "")))
            label = common["label"]
            if not image_url and not label and not icon_slug:
                continue
            normalized.append(
                {
                    **common,
                    "image_url": image_url,
                    "icon_slug": icon_slug,
                    "alt": raw.get("alt", label),
                    "url": raw.get("url", "/"),
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
    subtitle: str = "",
    actions: Any = None,
) -> dict[str, Any]:
    """Renderizza la barra titolo della pagina.

    Args:
        context: contesto template (non usato direttamente, riservato per
            estensioni v0.2 come breadcrumb dal request path).
        title: titolo principale della pagina (allineato a sinistra).
        subtitle: riga opzionale sopra il titolo (contesto o sezione).
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
        "subtitle": (subtitle or "").strip(),
        "actions": normalized_actions,
    }


_VALID_LOGO_SIZES = frozenset({"sm", "md", "lg"})


@register.inclusion_tag("velora_ui/components/layout/_velora_logo.html")
def velora_logo(
    image_url: str = "",
    label: str = "",
    url: str = "/",
    size: str = "md",
    alt: str = "",
    extra_class: str = "",
) -> dict[str, Any]:
    """Marchio standalone (immagine e/o testo). Richiede almeno uno dei due.

    Se sia `image_url` sia `label` sono vuoti dopo lo strip, il tag non emette
    markup (`show=False`).
    """

    img = (image_url or "").strip()
    lbl = (label or "").strip()
    if not img and not lbl:
        return {
            "show": False,
            "image_url": "",
            "label": "",
            "url": url or "/",
            "size": "md",
            "alt": "",
            "extra_class": extra_class or "",
        }
    sz = (size or "md").lower()
    if sz not in _VALID_LOGO_SIZES:
        sz = "md"
    alt_text = (alt or lbl).strip()
    return {
        "show": True,
        "image_url": img,
        "label": lbl,
        "url": url or "/",
        "size": sz,
        "alt": alt_text,
        "extra_class": extra_class or "",
    }
