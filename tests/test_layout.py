"""Test del template tag library `velora_layout` (M2 - Fase 4 del piano).

Coperti:
  - velora_header: render del tipo `link`
  - velora_header: render del tipo `user-menu`
  - velora_header: scarto silenzioso di item malformati
  - velora_header: app_name proviene dal context (context processor)
  - velora_title_bar: titolo presente
  - velora_title_bar: render delle azioni con varianti
  - velora_title_bar: nessun blocco azioni se actions vuoto

I test usano `Template.render(Context(...))` direttamente: non serve client
HTTP, non serve DB. `pytest-django` configura comunque l'environment via
`DJANGO_SETTINGS_MODULE = "velora_project.settings"` (vedi pyproject.toml).
"""

from __future__ import annotations

from django.template import Context, Template


def render(source: str, context: dict | None = None) -> str:
    """Render helper: crea Template + Context e ritorna la stringa renderizzata."""

    return Template(source).render(Context(context or {}))


# -- velora_header --------------------------------------------------------


def test_velora_header_renders_link_item():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [{"type": "link", "label": "Dashboard", "url": "/dashboard/"}],
            "velora_header_app_name": "App test",
        },
    )
    assert 'href="/dashboard/"' in html
    assert "Dashboard" in html
    assert "velora-header__item--link" in html


def test_velora_header_renders_user_menu_item():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [{"type": "user-menu", "label": "Mario Rossi", "url": "/me/"}],
            "velora_header_app_name": "App test",
        },
    )
    assert 'href="/me/"' in html
    assert "Mario Rossi" in html
    assert "velora-header__item--user" in html


def test_velora_header_skips_malformed_items():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {"type": "link", "label": "Ok", "url": "/"},
                "stringa-non-dict",
                {"type": "tipo-sconosciuto", "label": "X", "url": "/x/"},
                None,
            ],
            "velora_header_app_name": "App test",
        },
    )
    assert "Ok" in html
    assert "tipo-sconosciuto" not in html
    assert "stringa-non-dict" not in html


def test_velora_header_uses_app_name_from_context():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [],
            "velora_header_app_name": "Pannello Speciale",
        },
    )
    assert "Pannello Speciale" in html


def test_velora_header_falls_back_to_default_app_name():
    """Se il context non fornisce `velora_header_app_name`, il tag usa
    "Velora UI" hardcoded come fallback (non rompe il rendering).
    """
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {"items": []},
    )
    assert "Velora UI" in html


def test_velora_header_renders_app_icon_when_provided():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [],
            "velora_header_app_name": "X",
            "velora_header_app_icon_url": "/static/logo.svg",
        },
    )
    assert 'src="/static/logo.svg"' in html
    assert "velora-header__brand-icon" in html


def test_velora_header_marks_active_link_item():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {"type": "link", "label": "Home", "url": "/", "active": True},
                {"type": "link", "label": "Other", "url": "/o/"},
            ],
        },
    )
    # solo il primo item deve avere is-active
    assert html.count("is-active") == 1


# -- velora_header v0.2: single-menu --------------------------------------


def test_velora_header_renders_single_menu():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {
                    "type": "single-menu",
                    "label": "Account",
                    "items": [
                        {"label": "Profilo", "url": "/profile/"},
                        {"label": "Esci", "url": "/logout/"},
                    ],
                }
            ],
        },
    )
    assert "velora-header__item--single-menu" in html
    assert 'data-velora-component="header-menu"' in html
    assert 'aria-haspopup="true"' in html
    assert 'aria-expanded="false"' in html
    assert ">Account<" in html
    assert 'href="/profile/"' in html
    assert 'href="/logout/"' in html
    assert 'role="menu"' in html
    assert html.count('role="menuitem"') == 2


def test_velora_header_single_menu_align_right():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {
                    "type": "single-menu",
                    "label": "Settings",
                    "align": "right",
                    "items": [{"label": "Tema", "url": "/t"}],
                }
            ],
        },
    )
    assert 'data-velora-menu-align="right"' in html


def test_velora_header_single_menu_align_invalid_falls_back_to_left():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {
                    "type": "single-menu",
                    "label": "X",
                    "align": "diagonale",
                    "items": [{"label": "A", "url": "/a"}],
                }
            ],
        },
    )
    assert 'data-velora-menu-align="left"' in html


def test_velora_header_single_menu_skipped_if_no_items():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {"type": "single-menu", "label": "Vuoto", "items": []},
                {"type": "link", "label": "Sentinella", "url": "/s"},
            ],
        },
    )
    assert "Vuoto" not in html
    assert "Sentinella" in html


def test_velora_header_single_menu_filters_malformed_subitems():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {
                    "type": "single-menu",
                    "label": "Account",
                    "items": [
                        {"label": "Buono", "url": "/ok"},
                        "non-dict",
                        {"label": "Senza url"},
                        {"url": "/senza-label"},
                    ],
                }
            ],
        },
    )
    assert "Buono" in html
    assert "Senza url" not in html
    assert "/senza-label" not in html


# -- velora_header v0.2: multi-menu ---------------------------------------


def test_velora_header_renders_multi_menu_with_columns():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {
                    "type": "multi-menu",
                    "label": "Risorse",
                    "sections": [
                        {
                            "label": "Documentazione",
                            "items": [
                                {"label": "Quickstart", "url": "/d/q"},
                                {"label": "Guide", "url": "/d/g"},
                            ],
                        },
                        {
                            "label": "Supporto",
                            "items": [{"label": "Contatti", "url": "/c"}],
                        },
                    ],
                }
            ],
        },
    )
    assert "velora-header__item--multi-menu" in html
    assert "velora-header__menu-panel--multi" in html
    assert html.count("velora-header__multi-col") >= 2
    assert "Documentazione" in html
    assert "Supporto" in html
    assert 'href="/d/q"' in html
    assert 'href="/c"' in html


def test_velora_header_multi_menu_drops_empty_sections():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {
                    "type": "multi-menu",
                    "label": "Risorse",
                    "sections": [
                        {"label": "Vuota", "items": []},
                        {"label": "Piena", "items": [{"label": "Ok", "url": "/ok"}]},
                    ],
                }
            ],
        },
    )
    assert "Vuota" not in html
    assert "Piena" in html


def test_velora_header_multi_menu_skipped_if_no_valid_sections():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {"type": "multi-menu", "label": "Vuoto", "sections": []},
                {"type": "link", "label": "Sentinella", "url": "/s"},
            ],
        },
    )
    assert "Vuoto" not in html
    assert "Sentinella" in html


# -- velora_header v0.2: apps-menu ----------------------------------------


def test_velora_header_renders_apps_menu():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {
                    "type": "apps-menu",
                    "label": "App",
                    "apps": [
                        {"label": "Calendario", "url": "/cal", "color": "#4285f4"},
                        {"label": "Drive", "url": "/drive"},
                    ],
                }
            ],
        },
    )
    assert "velora-header__item--apps-menu" in html
    assert "velora-header__apps-grid" in html
    assert html.count("velora-header__app-tile") == 2
    assert "Calendario" in html
    assert 'href="/cal"' in html
    assert "--velora-app-tile-color: #4285f4" in html


def test_velora_header_apps_menu_skipped_if_no_apps():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {"type": "apps-menu", "label": "App", "apps": []},
                {"type": "link", "label": "Sentinella", "url": "/s"},
            ],
        },
    )
    assert "velora-header__item--apps-menu" not in html
    assert "Sentinella" in html


def test_velora_header_apps_menu_filters_malformed_apps():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {
                    "type": "apps-menu",
                    "label": "App",
                    "apps": [
                        {"label": "Ok", "url": "/o"},
                        {"label": "Senza url"},
                        "stringa",
                    ],
                }
            ],
        },
    )
    assert "Ok" in html
    assert "Senza url" not in html


# -- velora_header v0.2: notifications ------------------------------------


def test_velora_header_renders_notifications_with_unread_badge():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {
                    "type": "notifications",
                    "label": "Notifiche",
                    "unread_count": 3,
                    "items": [
                        {
                            "title": "Nuovo cliente",
                            "body": "Mario Rossi si e` registrato.",
                            "url": "/n/1",
                            "timestamp": "2 minuti fa",
                            "unread": True,
                        },
                        {"title": "Backup completato", "url": "/n/2"},
                    ],
                    "footer_label": "Vedi tutte",
                    "footer_url": "/notifications/",
                }
            ],
        },
    )
    assert "velora-header__item--notifications" in html
    assert "velora-header__notif-badge" in html
    assert ">3<" in html
    assert "Nuovo cliente" in html
    assert "Backup completato" in html
    assert "is-unread" in html
    assert html.count("is-unread") == 1
    assert "Vedi tutte" in html
    assert 'href="/notifications/"' in html


def test_velora_header_notifications_hides_badge_when_count_zero():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {
                    "type": "notifications",
                    "label": "Notifiche",
                    "unread_count": 0,
                    "items": [{"title": "Letta", "url": "/n/1"}],
                }
            ],
        },
    )
    assert "velora-header__notif-badge" not in html


def test_velora_header_notifications_shows_empty_label():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {
                    "type": "notifications",
                    "label": "Notifiche",
                    "items": [],
                    "empty_label": "Tutto in pari",
                }
            ],
        },
    )
    assert "velora-header__notif-empty" in html
    assert "Tutto in pari" in html


def test_velora_header_notifications_unread_count_invalid_falls_back_to_zero():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {
                    "type": "notifications",
                    "label": "Notifiche",
                    "unread_count": "tre",
                    "items": [{"title": "x", "url": "/x"}],
                }
            ],
        },
    )
    assert "velora-header__notif-badge" not in html


# -- velora_header v0.2: logo ---------------------------------------------


def test_velora_header_renders_logo_with_image_and_label():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {
                    "type": "logo",
                    "image_url": "/static/tenant.svg",
                    "label": "AcmeCorp",
                    "alt": "Acme",
                    "url": "/acme/",
                }
            ],
        },
    )
    assert "velora-header__item--logo" in html
    assert 'src="/static/tenant.svg"' in html
    assert 'alt="Acme"' in html
    assert "AcmeCorp" in html
    assert 'href="/acme/"' in html


def test_velora_header_logo_defaults_url_to_root():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {"items": [{"type": "logo", "label": "Brand"}]},
    )
    assert 'href="/"' in html
    assert "Brand" in html


def test_velora_header_logo_label_only_renders_without_image():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {"items": [{"type": "logo", "label": "TextOnly"}]},
    )
    assert "TextOnly" in html
    assert "velora-header__logo-img" not in html


def test_velora_header_logo_skipped_when_empty():
    html = render(
        "{% load velora_layout %}{% velora_header items=items %}",
        {
            "items": [
                {"type": "logo"},
                {"type": "link", "label": "Sentinella", "url": "/s"},
            ],
        },
    )
    assert "velora-header__item--logo" not in html
    assert "Sentinella" in html


# -- velora_title_bar -----------------------------------------------------


def test_velora_title_bar_renders_title():
    html = render(
        "{% load velora_layout %}{% velora_title_bar title='Dashboard' %}",
    )
    assert "Dashboard" in html
    assert "velora-title-bar__title" in html


def test_velora_title_bar_renders_actions_with_variants():
    html = render(
        "{% load velora_layout %}{% velora_title_bar title=t actions=a %}",
        {
            "t": "Pagina",
            "a": [
                {"label": "Annulla", "url": "/cancel/", "variant": "secondary"},
                {"label": "Salva", "url": "/save/", "variant": "primary"},
            ],
        },
    )
    assert "Annulla" in html
    assert "Salva" in html
    assert 'href="/cancel/"' in html
    assert 'href="/save/"' in html
    assert "velora-btn--primary" in html
    assert "velora-btn--secondary" in html


def test_velora_title_bar_omits_actions_block_when_empty():
    html = render(
        "{% load velora_layout %}{% velora_title_bar title='X' %}",
    )
    assert "velora-title-bar__actions" not in html


def test_velora_title_bar_defaults_action_variant_to_secondary():
    html = render(
        "{% load velora_layout %}{% velora_title_bar title=t actions=a %}",
        {
            "t": "P",
            "a": [{"label": "Solo", "url": "/x/"}],
        },
    )
    assert "velora-btn--secondary" in html


# -- velora_logo -----------------------------------------------------------


def test_velora_logo_renders_label_only():
    html = render(
        "{% load velora_layout %}{% velora_logo label='Acme' url='/a/' %}",
    )
    assert "velora-logo" in html
    assert "Acme" in html
    assert 'href="/a/"' in html
    assert "<img" not in html


def test_velora_logo_renders_image_and_label():
    html = render(
        "{% load velora_layout %}"
        "{% velora_logo image_url='/x.svg' label='Co' url='/' alt='Logo' %}",
    )
    assert 'src="/x.svg"' in html
    assert "Co" in html
    assert 'alt="Logo"' in html


def test_velora_logo_empty_when_no_image_and_no_label():
    html = render(
        "{% load velora_layout %}{% velora_logo image_url='' label='' %}",
    )
    assert "velora-logo" not in html


def test_velora_logo_invalid_size_falls_back_to_md():
    html = render(
        "{% load velora_layout %}{% velora_logo label='X' size='huge' %}",
    )
    assert "velora-logo--md" in html
    assert "velora-logo--huge" not in html


# -- context processor ----------------------------------------------------


def test_header_defaults_context_processor_returns_defaults():
    """Il context processor deve esporre i default del pacchetto quando il
    progetto host non sovrascrive le voci `VELORA_*`.
    """
    from velora_ui.context_processors import header_defaults

    ctx = header_defaults(request=None)
    assert ctx["velora_header_app_name"] == "Velora UI"
    assert ctx["velora_header_app_icon_url"] is None


def test_header_defaults_context_processor_picks_up_overrides(settings):
    """Se il progetto host ridefinisce le voci `VELORA_*`, il context
    processor deve riflettere l'override.
    """
    from velora_ui.context_processors import header_defaults

    settings.VELORA_HEADER_APP_NAME = "Override App"
    settings.VELORA_HEADER_APP_ICON_URL = "/o.svg"

    ctx = header_defaults(request=None)
    assert ctx["velora_header_app_name"] == "Override App"
    assert ctx["velora_header_app_icon_url"] == "/o.svg"
