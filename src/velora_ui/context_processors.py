"""Context processor di Velora UI.

Inietta nel contesto template le voci necessarie ai tag di layout in modo che
il progetto host non debba ripeterle in ogni view. Per attivarli, aggiungere
``velora_ui.context_processors.header_defaults`` in
``TEMPLATES[*].OPTIONS.context_processors``.

Voci esposte:

  - ``velora_header_app_name`` -> da ``VELORA_HEADER_APP_NAME``
  - ``velora_header_app_icon_url`` -> da ``VELORA_HEADER_APP_ICON_URL``

Le view sono libere di sovrascriverle passando le stesse chiavi nel context.
"""

from __future__ import annotations

from typing import Any

from .settings import get_setting


def header_defaults(request: Any) -> dict[str, Any]:  # noqa: ARG001 - signature Django
    """Espone i default di branding dell'header al template engine."""

    return {
        "velora_header_app_name": get_setting("VELORA_HEADER_APP_NAME"),
        "velora_header_app_icon_url": get_setting("VELORA_HEADER_APP_ICON_URL"),
    }
