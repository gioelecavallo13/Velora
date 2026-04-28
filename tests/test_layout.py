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
