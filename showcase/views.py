from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from velora_ui import __version__ as velora_version


_TOAST_DEMO_LEVELS = {
    "success": (messages.SUCCESS, "Toast emesso da django.contrib.messages (success)"),
    "error": (messages.ERROR, "Toast emesso da django.contrib.messages (error)"),
    "warning": (messages.WARNING, "Toast emesso da django.contrib.messages (warning)"),
    "info": (messages.INFO, "Toast emesso da django.contrib.messages (info)"),
}


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

    # Sidebar dello showcase = indice cliccabile delle sezioni della pagina.
    # Aggiungere una sezione qui ed in showcase/index.html mantiene la TOC
    # in sync con il contenuto.
    sidebar_items = [
        {"label": "Overview", "url": "#overview", "icon": "·"},
        {"label": "Layout", "url": "#layout", "icon": "L"},
        {"label": "Form", "url": "#form", "icon": "F"},
        {"label": "Tabelle", "url": "#tables", "icon": "T"},
        {"label": "Link", "url": "#links", "icon": "→"},
        {"label": "Feedback", "url": "#feedback", "icon": "!"},
    ]

    title_actions = [
        {"label": "Documentazione", "url": "#", "variant": "secondary"},
        {"label": "Nuovo elemento", "url": "#", "variant": "primary"},
    ]

    role_choices = [
        ("admin", "Amministratore"),
        ("editor", "Editor"),
        ("viewer", "Sola lettura"),
    ]

    plan_choices = [
        {"value": "free", "label": "Free"},
        {"value": "pro", "label": "Pro"},
        {"value": "enterprise", "label": "Enterprise", "disabled": True},
    ]

    table_headers = [
        {"key": "id", "label": "#", "width": "60px", "align": "right"},
        {"key": "name", "label": "Nome"},
        {"key": "email", "label": "Email"},
        {"key": "role", "label": "Ruolo"},
        {"key": "amount", "label": "Importo", "align": "right"},
    ]
    table_rows = [
        {"id": 1, "name": "Mario Rossi", "email": "mario@example.com", "role": "Admin", "amount": "€ 1.250,00"},
        {"id": 2, "name": "Luca Bianchi", "email": "luca@example.com", "role": "Editor", "amount": "€ 480,50"},
        {"id": 3, "name": "Giulia Verdi", "email": "giulia@example.com", "role": "Viewer", "amount": "€ 0,00"},
        {"id": 4, "name": "Anna Neri", "email": "anna@example.com", "role": "Editor", "amount": "€ 2.100,75"},
    ]
    table_page = {"number": 2, "num_pages": 12}

    # Demo del pattern django messages -> velora_toast_messages.
    # Aggiungere ?toast=success|error|warning|info alla URL emette un
    # messaggio del livello corrispondente; il template base.html lo
    # converte automaticamente in toast Velora.
    requested_toast = request.GET.get("toast", "")
    if requested_toast in _TOAST_DEMO_LEVELS:
        level, text = _TOAST_DEMO_LEVELS[requested_toast]
        messages.add_message(request, level, text)

    return render(
        request,
        "showcase/index.html",
        context={
            "velora_version": velora_version,
            "showcase_header_items": header_items,
            "showcase_sidebar_items": sidebar_items,
            "showcase_title_actions": title_actions,
            "showcase_role_choices": role_choices,
            "showcase_plan_choices": plan_choices,
            "showcase_table_headers": table_headers,
            "showcase_table_rows": table_rows,
            "showcase_table_page": table_page,
        },
    )
