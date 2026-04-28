from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from velora_ui import __version__ as velora_version


def index(request: HttpRequest) -> HttpResponse:
    """Pagina placeholder dello showcase + smoke test M2.

    Espone al template:
      - velora_version              : versione del pacchetto
      - showcase_header_items       : item dell'header (link + user-menu)
      - showcase_sidebar_items      : voci di sidebar di esempio
      - showcase_title_actions      : azioni della title bar

    I dati sono statici per il momento; in M6 (Fase 8) lo showcase
    diventera` un catalogo vivente con sotto-pagine dedicate.
    """

    header_items = [
        {"type": "link", "label": "Showcase", "url": "/", "active": True},
        {"type": "link", "label": "Documentazione", "url": "#"},
        {"type": "user-menu", "label": "Sviluppatore", "url": "#"},
    ]

    sidebar_items = [
        {"label": "Layout", "url": "#layout", "icon": "L", "active": True},
        {"label": "Form", "url": "#form", "icon": "F"},
        {"label": "Tabelle", "url": "#tables", "icon": "T"},
        {"label": "Feedback", "url": "#feedback", "icon": "!"},
        {"label": "Settings", "url": "#settings", "icon": "S"},
    ]

    title_actions = [
        {"label": "Documentazione", "url": "#", "variant": "secondary"},
        {"label": "Nuovo elemento", "url": "#", "variant": "primary"},
    ]

    return render(
        request,
        "showcase/index.html",
        context={
            "velora_version": velora_version,
            "showcase_header_items": header_items,
            "showcase_sidebar_items": sidebar_items,
            "showcase_title_actions": title_actions,
        },
    )
