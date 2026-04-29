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
