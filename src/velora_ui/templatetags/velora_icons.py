"""Template tag per risorse icone (Fase 12 — `velora_icons`)."""

from __future__ import annotations

from typing import Any

from django import template
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.inclusion_tag(
    "velora_ui/components/icons/_ionicons_gallery.html",
    takes_context=True,
)
def velora_ionicons_gallery(
    context: template.Context,
    search_input_id: str = "velora-ionicons-search",
    search_placeholder: str = "",
    search_label: str = "",
) -> dict[str, Any]:
    """Galleria Ionicons statica: manifest JSON + SVG serviti da ``staticfiles``."""

    del context
    base = static("velora_ui/icons/ionicons/")
    if not base.endswith("/"):
        base += "/"
    ph = (search_placeholder or "").strip()
    lb = (search_label or "").strip()
    return {
        "manifest_url": static("velora_ui/icons/ionicons-manifest.json"),
        "icons_base_url": base,
        "search_input_id": search_input_id,
        "search_placeholder": ph or _("Cerca icona…"),
        "search_label": lb or _("Cerca nelle Ionicons"),
    }
