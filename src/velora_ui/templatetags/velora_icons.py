"""Template tag per risorse icone (Fase 12 — `velora_icons`)."""

from __future__ import annotations

import functools
import re
from pathlib import Path
from typing import Any

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.utils.html import escape
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext_lazy as _

register = template.Library()

_SLUG_SAFE = re.compile(r"^[a-z0-9][a-z0-9-]{0,119}$")

_SIZE_PX = {"sm": 18, "md": 22, "lg": 28, "xl": 36}


def _normalize_slug(name: str) -> str:
    slug = (name or "").strip().removesuffix(".svg").lower()
    if not slug or not _SLUG_SAFE.fullmatch(slug):
        return ""
    return slug


def _prepare_svg(raw: str) -> str:
    """Inject Velora / Ionicons-compat styling hooks on the root ``<svg>``."""
    raw = raw.strip()
    m = re.match(r"<svg(\s[^>]*?)>", raw, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    head = m.group(1)
    head = re.sub(r'\s+width\s*=\s*"[^"]*"', "", head, flags=re.I)
    head = re.sub(r"\s+width\s*=\s*'[^']*'", "", head, flags=re.I)
    head = re.sub(r'\s+height\s*=\s*"[^"]*"', "", head, flags=re.I)
    head = re.sub(r"\s+height\s*=\s*'[^']*'", "", head, flags=re.I)

    if re.search(r'\bclass="', head, re.I):
        head = re.sub(
            r'class="([^"]*)"',
            lambda mm: f'class="velora-icon__svg {mm.group(1)}"',
            head,
            count=1,
        )
    elif re.search(r"\bclass='", head, re.I):
        head = re.sub(
            r"class='([^']*)'",
            lambda mm: f"class='velora-icon__svg {mm.group(1)}'",
            head,
            count=1,
        )
    else:
        head = ' class="velora-icon__svg ionicon"' + head

    low = head.lower()
    if "focusable=" not in low:
        head += ' focusable="false"'
    if "preserveaspectratio=" not in low:
        head += ' preserveAspectRatio="xMidYMid meet"'
    head += ' width="100%" height="100%"'
    return f"<svg{head}>" + raw[m.end():]


@functools.lru_cache(maxsize=512)
def _inline_svg_markup(slug: str) -> str:
    rel = f"velora_ui/icons/ionicons/{slug}.svg"
    path = finders.find(rel)
    if not path:
        return ""
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError:
        return ""
    return _prepare_svg(raw)


def _render_img_tag(
    slug: str,
    extra_class: str,
    alt: str,
    w: int,
    h: int,
) -> SafeString:
    url = static(f"velora_ui/icons/ionicons/{slug}.svg")
    escaped_alt = escape(alt or "")
    cls = escape((extra_class or "").strip())
    cls_attr = f' class="{cls}"' if cls else ""
    return mark_safe(
        f'<img src="{escape(url)}" width="{w}" height="{h}" alt="{escaped_alt}"'
        f"{cls_attr} loading=\"lazy\" decoding=\"async\" />"
    )


@register.simple_tag
def velora_icon(
    name: str = "",
    extra_class: str = "",
    alt: str = "",
    width: int | str = 22,
    height: int | str = 22,
    size: str = "",
    as_img: bool = False,
) -> SafeString:
    """Ionicons come SVG inline (default) o ``<img>`` se ``as_img=True``.

    Gli SVG vengono letti da ``static/velora_ui/icons/ionicons/<slug>.svg`` (sync
    da npm: ``npm run sync:icons``). L'inline SVG usa ``currentColor`` così
    dimensione, colore, hover e dark mode seguono il CSS del contenitore
    (variabile opzionale ``--velora-icon-color`` sul wrapper ``.velora-icon``).

    Parametri ``size``: ``sm`` / ``md`` / ``lg`` / ``xl`` (override di width/height
    se indicato). Con ``alt`` non vuoto il wrapper espone ``role="img"`` e
    ``aria-label``; altrimenti ``aria-hidden="true"`` (adatto alle icone decorative).
    """

    slug = _normalize_slug(name)
    if not slug:
        return mark_safe("")

    sz = (size or "").strip().lower()
    if sz in _SIZE_PX:
        w = h = _SIZE_PX[sz]
    else:
        try:
            w = int(width)
        except (TypeError, ValueError):
            w = 22
        try:
            h = int(height)
        except (TypeError, ValueError):
            h = w

    if as_img:
        return _render_img_tag(slug, extra_class, alt, w, h)

    svg = _inline_svg_markup(slug)
    if not svg:
        return mark_safe("")

    wrapper_classes = "velora-icon"
    if extra_class.strip():
        wrapper_classes += " " + extra_class.strip()
    class_html = escape(wrapper_classes)
    alt_stripped = (alt or "").strip()
    if alt_stripped:
        a11y = f' role="img" aria-label="{escape(alt_stripped)}"'
    else:
        a11y = ' aria-hidden="true"'
    return mark_safe(
        f'<span class="{class_html}" style="width:{w}px;height:{h}px"{a11y}>{svg}</span>'
    )


@register.inclusion_tag(
    "velora_ui/components/icons/_ionicons_gallery.html",
    takes_context=True,
)
def velora_ionicons_gallery(
    context: template.Context,
    search_input_id: str = "velora-ionicons-search",
    search_placeholder: str = "",
    search_label: str = "",
    search_url: str = "",
    section_title: str = "",
    hint: str = "",
) -> dict[str, Any]:
    """Galleria Ionicons: manifest + SVG statici; ricerca opzionale via ``search_url`` (AJAX)."""

    del context
    base = static("velora_ui/icons/ionicons/")
    if not base.endswith("/"):
        base += "/"
    ph = (search_placeholder or "").strip()
    lb = (search_label or "").strip()
    title = (section_title or "").strip() or _("Ionicons")
    hint_t = (hint or "").strip() or _(
        "Per vedere tutte le icone scrivi «tutte» nella ricerca."
    )
    copy_hint = _("Copia slug negli appunti")
    return {
        "manifest_url": static("velora_ui/icons/ionicons-manifest.json"),
        "icons_base_url": base,
        "search_input_id": search_input_id,
        "search_placeholder": ph or _("Cerca icona…"),
        "search_label": lb or _("Cerca nelle Ionicons"),
        "search_url": (search_url or "").strip(),
        "section_title": title,
        "hint": hint_t,
        "copy_hint": copy_hint,
    }
