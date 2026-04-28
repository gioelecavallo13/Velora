"""Test della templatetag library `velora_overlays` (Fase 10).

Coperti:
  - velora_tooltip (10.3)
"""

from __future__ import annotations

from django.template import Context, Template


def render(source: str, context: dict | None = None) -> str:
    return Template(source).render(Context(context or {}))


def test_tooltip_emits_data_attributes():
    html = render(
        "{% load velora_overlays %}<button {% velora_tooltip 'Modifica cliente' %}>X</button>"
    )
    assert 'data-velora-component="tooltip"' in html
    assert 'data-tooltip-text="Modifica cliente"' in html
    assert 'data-tooltip-placement="top"' in html
    assert 'data-tooltip-delay="200"' in html


def test_tooltip_placement_and_delay_overrides():
    html = render(
        "{% load velora_overlays %}<a {% velora_tooltip 'Salva' placement='bottom' delay=500 %}>X</a>"
    )
    assert 'data-tooltip-placement="bottom"' in html
    assert 'data-tooltip-delay="500"' in html


def test_tooltip_invalid_placement_falls_back_to_top():
    html = render(
        "{% load velora_overlays %}<a {% velora_tooltip 'X' placement='upside-down' %}>Z</a>"
    )
    assert 'data-tooltip-placement="top"' in html


def test_tooltip_negative_delay_clamped_to_zero():
    html = render(
        "{% load velora_overlays %}<a {% velora_tooltip 'X' delay=-100 %}>Z</a>"
    )
    assert 'data-tooltip-delay="0"' in html


def test_tooltip_empty_text_emits_nothing():
    html = render("{% load velora_overlays %}<a {% velora_tooltip '' %}>Z</a>")
    assert "data-velora-component" not in html
    assert "data-tooltip-text" not in html


def test_tooltip_escapes_text_to_avoid_break_out():
    html = render(
        "{% load velora_overlays %}<a {% velora_tooltip text %}>Z</a>",
        {"text": '"><script>alert(1)</script>'},
    )
    assert "<script>" not in html
    assert "&quot;&gt;&lt;script&gt;" in html or "&#x27;" in html or "&lt;script&gt;" in html
