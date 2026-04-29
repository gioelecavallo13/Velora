"""Test per `velora_icons` (Fase 12 — galleria Ionicons)."""

from __future__ import annotations

from django.template import Context, Template


def render(source: str, context: dict | None = None) -> str:
    return Template(source).render(Context(context or {}))


def test_velora_ionicons_gallery_renders_shell() -> None:
    html = render(
        "{% load velora_icons %}{% velora_ionicons_gallery search_input_id='gx1' %}",
    )
    assert "velora-ionicons-gallery" in html
    assert "data-velora-component=\"ionicons-gallery\"" in html
    assert "ionicons-manifest.json" in html
    assert "/velora_ui/icons/ionicons/" in html or "icons/ionicons/" in html
    assert 'id="gx1"' in html
    assert "velora-ionicons-gallery__hint" in html
    assert "velora-ionicons-gallery__title" in html


def test_velora_ionicons_gallery_emits_search_url() -> None:
    html = render(
        "{% load velora_icons %}"
        "{% velora_ionicons_gallery search_input_id='g2' search_url='/api/ionicons/' %}",
    )
    assert 'data-search-url="/api/ionicons/"' in html


def test_velora_icon_inline_renders_svg_wrapper() -> None:
    html = render(
        "{% load velora_icons %}{% velora_icon 'home-outline' %}",
    )
    assert 'class="velora-icon"' in html
    assert "velora-icon__svg" in html
    assert "<path" in html
    assert 'aria-hidden="true"' in html


def test_velora_icon_with_aria_label_when_alt_set() -> None:
    html = render(
        "{% load velora_icons %}{% velora_icon 'home-outline' alt='Home' %}",
    )
    assert 'role="img"' in html
    assert "aria-label=" in html
    assert "Home" in html


def test_velora_icon_as_img() -> None:
    html = render(
        "{% load velora_icons %}{% velora_icon 'home-outline' as_img=True %}",
    )
    assert html.strip().startswith("<img ")
    assert "home-outline.svg" in html


def test_velora_icon_invalid_name_empty() -> None:
    html = render(
        "{% load velora_icons %}{% velora_icon '' %}{% velora_icon '../etc/passwd' %}",
    )
    assert html.strip() == ""


def test_velora_icon_escapes_extra_class() -> None:
    html = render(
        "{% load velora_icons %}{% velora_icon 'home-outline' extra_class='foo bar' %}",
    )
    assert 'class="velora-icon foo bar"' in html
    assert "<script>" not in html
