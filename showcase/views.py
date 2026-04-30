import json
from pathlib import Path

from django.contrib import messages
from django.contrib.staticfiles import finders
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from velora_ui import __version__ as velora_version


_IONICONS_INITIAL = 96
_IONICONS_LIMIT_MAX = 2000
_IONICONS_MANIFEST_REL = "velora_ui/icons/ionicons-manifest.json"

_manifest_mtime: float | None = None
_manifest_slugs: list[str] | None = None


def _ionicons_manifest_slugs() -> list[str]:
    """Slug ordinati dal manifest statico; cache invalidata se il file cambia."""

    global _manifest_mtime, _manifest_slugs
    path = finders.find(_IONICONS_MANIFEST_REL)
    if not path:
        return []
    p = Path(path)
    try:
        mtime = p.stat().st_mtime
    except OSError:
        return []
    if _manifest_slugs is not None and _manifest_mtime == mtime:
        return _manifest_slugs
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _manifest_slugs = []
        _manifest_mtime = mtime
        return _manifest_slugs
    _manifest_slugs = raw if isinstance(raw, list) else []
    _manifest_mtime = mtime
    return _manifest_slugs


def ionicons_search(request: HttpRequest) -> JsonResponse:
    """Ricerca AJAX sul catalogo Ionicons (slug kebab-case, Ionicons 7)."""

    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    q = (request.GET.get("q") or "").strip().lower()
    if len(q) > 80:
        q = q[:80]

    try:
        limit = int(request.GET.get("limit", "240"))
    except ValueError:
        limit = 240
    limit = max(1, min(limit, _IONICONS_LIMIT_MAX))

    slugs = _ionicons_manifest_slugs()
    total_icons = len(slugs)
    if total_icons == 0:
        return JsonResponse(
            {
                "icons": [],
                "total_icons": 0,
                "matched": 0,
                "returned": 0,
                "truncated": False,
                "error": "manifest_missing",
            }
        )

    tutte_keys = {"tutte", "all", "*"}
    if q in tutte_keys:
        filtered = slugs
    elif q:
        filtered = [s for s in slugs if q in s.lower()]
    else:
        filtered = slugs[:_IONICONS_INITIAL]

    matched = len(filtered)
    out = filtered[:limit]
    return JsonResponse(
        {
            "icons": out,
            "total_icons": total_icons,
            "matched": matched,
            "returned": len(out),
            "truncated": matched > len(out),
            "is_initial": not q,
        }
    )


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

    # Header demo dei tipi item v0.1 + v0.2.
    # Nello showcase carichiamo l'header con uno di ogni tipo per dimostrare
    # i nuovi pannelli (single-menu, multi-menu, apps-menu, notifications) e
    # il logo aggiuntivo. Su pagine reali un header tipico ne usa meno.
    header_items = [
        {"type": "link", "label": "Showcase", "url": "/", "active": True},
        {
            "type": "single-menu",
            "label": "Documentazione",
            "items": [
                {"label": "Quickstart", "url": "#overview"},
                {"label": "Componenti", "url": "#layout"},
                {"label": "API JS", "url": "#feedback"},
            ],
        },
        {
            "type": "multi-menu",
            "label": "Risorse",
            "sections": [
                {
                    "label": "Sviluppo",
                    "items": [
                        {"label": "Form", "url": "#form"},
                        {"label": "Tabelle", "url": "#tables"},
                        {"label": "Link", "url": "#links"},
                    ],
                },
                {
                    "label": "Community",
                    "items": [
                        {"label": "Repository", "url": "https://github.com/gioelecavallo13/Velora"},
                        {"label": "Changelog", "url": "#"},
                    ],
                },
            ],
        },
        {
            "type": "logo",
            "image_url": "",
            "label": "Demo Tenant",
            "url": "#overview",
        },
        {
            "type": "apps-menu",
            "label": "App",
            "icon_slug": "apps-sharp",
            "apps": [
                {"label": "Calendario", "url": "#", "color": "#4285f4"},
                {"label": "Drive", "url": "#", "color": "#34a853"},
                {"label": "Mail", "url": "#", "color": "#ea4335"},
                {"label": "Note", "url": "#", "color": "#fbbc05"},
                {"label": "Foto", "url": "#", "color": "#c1282e"},
                {"label": "Contatti", "url": "#", "color": "#7AB55C"},
            ],
        },
        {
            "type": "notifications",
            "label": "Notifiche",
            "unread_count": 3,
            "icon_slug": "notifications-sharp",
            "items": [
                {
                    "title": "Nuovo cliente registrato",
                    "body": "Mario Rossi ha completato l'onboarding.",
                    "url": "#",
                    "timestamp": "2 minuti fa",
                    "unread": True,
                },
                {
                    "title": "Backup completato",
                    "body": "Snapshot serale eseguito senza errori.",
                    "url": "#",
                    "timestamp": "1 ora fa",
                    "unread": True,
                },
                {
                    "title": "Aggiornamento disponibile",
                    "url": "#",
                    "timestamp": "Ieri",
                    "unread": True,
                },
                {
                    "title": "Pagamento ricevuto",
                    "body": "Fattura #2024-018 saldata.",
                    "url": "#",
                    "timestamp": "2 giorni fa",
                },
            ],
            "footer_label": "Vedi tutte",
            "footer_url": "#",
        },
        {
            "type": "user-menu",
            "label": _("Utente"),
            "url": "#",
            "icon_slug": "person-sharp",
            "items": [
                {"label": _("Impostazioni"), "url": "#"},
                {"label": _("Esci"), "url": "#"},
            ],
        },
    ]

    # Sidebar dello showcase = indice cliccabile delle sezioni della pagina.
    # Aggiungere una sezione qui ed in showcase/index.html mantiene la TOC
    # in sync con il contenuto.
    # Sidebar: Ionicons + link semplici + ramo con sottomenu (flyout).
    sidebar_items = [
        {
            "label": _("Panoramica"),
            "url": "#overview",
            "icon_slug": "home-outline",
        },
        {
            "label": _("Contenuti showcase"),
            "icon_slug": "library-outline",
            "children": [
                {"label": _("Scelte tipografiche"), "url": "#typography"},
                {"label": _("Layout"), "url": "#layout"},
                {"label": _("Form"), "url": "#form"},
                {"label": _("Tabelle"), "url": "#tables"},
                {"label": _("Link"), "url": "#links"},
                {"label": _("Feedback"), "url": "#feedback"},
                {"label": _("Navigazione"), "url": "#navigation"},
                {"label": _("Overlay"), "url": "#overlays"},
                {"label": _("Avanzamento"), "url": "#progress"},
                {"label": _("Form avanzati"), "url": "#form-advanced"},
                {"label": _("Tabelle interattive"), "url": "#tables-advanced"},
                {"label": _("Checkbox"), "url": "#checkbox"},
                {"label": _("Grafici"), "url": "#chart"},
                {"label": _("Ionicons"), "url": "#ionicons"},
                {"label": _("Tema e marchio"), "url": "#theme-brand"},
            ],
        },
    ]

    title_actions = [
        {"label": _("Guida rapida"), "url": "#overview", "variant": "secondary"},
        {"label": _("Nuova bozza"), "url": "#form", "variant": "primary"},
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

    # Dati tabella per {% velora_chart_from_table %}: stesso schema thead/tbody del parser JS.
    chart_table_headers = [
        {"key": "country", "label": ""},
        {"key": "q1", "label": "Q1"},
        {"key": "q2", "label": "Q2"},
        {"key": "q3", "label": "Q3"},
    ]
    chart_table_rows = [
        {"country": _("Italia"), "q1": 10, "q2": 20, "q3": 15},
        {"country": _("Germania"), "q1": 5, "q2": 8, "q3": 12},
        {"country": _("Spagna"), "q1": 8, "q2": 7, "q3": 9},
    ]

    # ---- v0.2 - Fase 10 ------------------------------------------------

    # Breadcrumb di esempio: Home > Sezione > Pagina corrente
    breadcrumb_items = [
        {"label": "Showcase", "url": "/"},
        {"label": "Componenti v0.2", "url": "#layout"},
        {"label": "Pagina corrente"},
    ]

    # Submenu di esempio: link con stato active
    submenu_items = [
        {"label": "Generale", "url": "#overview", "active": True},
        {"label": "Tema", "url": "#layout"},
        {"label": "Sicurezza", "url": "#feedback"},
        {"label": "Notifiche", "url": "#feedback"},
        {"label": "Esporta dati", "url": "#tables"},
    ]

    # Drop-down items per gli esempi inline
    dropdown_items = [
        {"label": "Modifica", "url": "#"},
        {"label": "Duplica", "url": "#"},
        {"label": "Archivia", "url": "#"},
    ]

    # Step del wizard di esempio (currente = 2)
    wizard_steps = [
        "Anagrafica",
        "Indirizzo",
        "Pagamento",
        "Conferma",
    ]

    # ---- v0.3 - Fase 11 ------------------------------------------------

    # Locale autocomplete: lista statica di esempio
    autocomplete_options = [
        {"value": "rm", "label": "Roma"},
        {"value": "mi", "label": "Milano"},
        {"value": "to", "label": "Torino"},
        {"value": "na", "label": "Napoli"},
        {"value": "fi", "label": "Firenze"},
        {"value": "bo", "label": "Bologna"},
        {"value": "ve", "label": "Venezia"},
        {"value": "ge", "label": "Genova"},
        {"value": "ba", "label": "Bari"},
        {"value": "pa", "label": "Palermo"},
    ]

    multiselect_options = [
        {"value": "frontend", "label": "Frontend"},
        {"value": "backend", "label": "Backend"},
        {"value": "devops", "label": "DevOps"},
        {"value": "ux", "label": "UX/UI"},
        {"value": "qa", "label": "QA/Testing"},
    ]

    # Tabella interattiva con form-in-cell
    advanced_table_headers = [
        {"key": "id", "label": "#", "width": "60px", "align": "right"},
        {"key": "name", "label": "Nome", "width": "180px"},
        {"key": "role", "label": "Ruolo"},
        {"key": "active", "label": "Attivo", "width": "70px", "align": "center"},
        {"key": "tier", "label": "Piano"},
    ]
    advanced_table_rows = [
        {
            "id": 1,
            "name": {
                "value": "Mario Rossi",
                "form_in_cell": {
                    "type": "text",
                    "name": "name",
                    "value": "Mario Rossi",
                    "url": "/api/users/1/",
                    "row_id": 1,
                },
            },
            "role": {
                "value": "Admin",
                "form_in_cell": {
                    "type": "select",
                    "name": "role",
                    "value": "admin",
                    "url": "/api/users/1/",
                    "row_id": 1,
                    "choices": [("admin", "Admin"), ("editor", "Editor"), ("viewer", "Viewer")],
                },
            },
            "active": {
                "value": True,
                "form_in_cell": {
                    "type": "onoff",
                    "name": "active",
                    "value": True,
                    "url": "/api/users/1/",
                    "row_id": 1,
                },
            },
            "tier": "Pro",
        },
        {
            "id": 2,
            "name": {
                "value": "Luca Bianchi",
                "form_in_cell": {
                    "type": "text",
                    "name": "name",
                    "value": "Luca Bianchi",
                    "url": "/api/users/2/",
                    "row_id": 2,
                },
            },
            "role": {
                "value": "Editor",
                "form_in_cell": {
                    "type": "select",
                    "name": "role",
                    "value": "editor",
                    "url": "/api/users/2/",
                    "row_id": 2,
                    "choices": [("admin", "Admin"), ("editor", "Editor"), ("viewer", "Viewer")],
                },
            },
            "active": {
                "value": False,
                "form_in_cell": {
                    "type": "onoff",
                    "name": "active",
                    "value": False,
                    "url": "/api/users/2/",
                    "row_id": 2,
                },
            },
            "tier": "Free",
        },
        {
            "id": 3,
            "name": {
                "value": "Giulia Verdi",
                "form_in_cell": {
                    "type": "text",
                    "name": "name",
                    "value": "Giulia Verdi",
                    "url": "/api/users/3/",
                    "row_id": 3,
                },
            },
            "role": {
                "value": "Viewer",
                "form_in_cell": {
                    "type": "select",
                    "name": "role",
                    "value": "viewer",
                    "url": "/api/users/3/",
                    "row_id": 3,
                    "choices": [("admin", "Admin"), ("editor", "Editor"), ("viewer", "Viewer")],
                },
            },
            "active": {
                "value": True,
                "form_in_cell": {
                    "type": "onoff",
                    "name": "active",
                    "value": True,
                    "url": "/api/users/3/",
                    "row_id": 3,
                },
            },
            "tier": "Pro",
        },
    ]

    bulk_actions = [
        {"label": "Archivia", "value": "archive", "variant": "secondary"},
        {
            "label": "Elimina",
            "value": "delete",
            "variant": "danger",
            "confirm": "Eliminare le righe selezionate? L'operazione e` irreversibile.",
        },
    ]

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
            "showcase_ionicons_search_url": reverse("showcase:ionicons_search"),
            "showcase_header_items": header_items,
            "showcase_sidebar_items": sidebar_items,
            "showcase_sidebar_brand_full": "APP",
            "showcase_sidebar_brand_short": "AP",
            "showcase_sidebar_show_search": True,
            "showcase_title_bar_title": _("Velora UI Showcase"),
            "showcase_title_actions": title_actions,
            "showcase_role_choices": role_choices,
            "showcase_plan_choices": plan_choices,
            "showcase_table_headers": table_headers,
            "showcase_table_rows": table_rows,
            "showcase_table_page": table_page,
            "showcase_chart_table_headers": chart_table_headers,
            "showcase_chart_table_rows": chart_table_rows,
            "showcase_breadcrumb_items": breadcrumb_items,
            "showcase_submenu_items": submenu_items,
            "showcase_dropdown_items": dropdown_items,
            "showcase_wizard_steps": wizard_steps,
            "showcase_autocomplete_options": autocomplete_options,
            "showcase_multiselect_options": multiselect_options,
            "showcase_advanced_table_headers": advanced_table_headers,
            "showcase_advanced_table_rows": advanced_table_rows,
            "showcase_bulk_actions": bulk_actions,
        },
    )
