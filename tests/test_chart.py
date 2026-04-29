"""Test di `velora_ui.chartutils` e template tag `velora_chart` (Fase 12.1)."""

from __future__ import annotations

import pytest
from django.template import Context, Template

from velora_ui.chartutils import normalize_chart_type, VALID_CHART_TYPES


def test_normalize_chart_type_defaults() -> None:
    assert normalize_chart_type("") == "line"
    assert normalize_chart_type(None) == "line"  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("line", "line"),
        ("LINE", "line"),
        ("bar", "bar"),
        ("pie", "pie"),
        ("pIe", "pie"),
        ("area", "line"),
        ("", "line"),
    ],
)
def test_normalize_chart_type_mapping(raw: str, expected: str) -> None:
    assert normalize_chart_type(raw) == expected


def test_valid_chart_types_frozen() -> None:
    assert VALID_CHART_TYPES == {"line", "bar", "pie"}


def _render_chart(**kwargs) -> str:
    bits = " ".join(f'{k}="{v}"' for k, v in kwargs.items())
    return Template(
        "{% load velora_chart %}{% velora_chart_from_table " + bits + " %}"
    ).render(Context({}))


def test_velora_chart_from_table_empty_selector() -> None:
    assert _render_chart(table_selector="").strip() == ""
    assert _render_chart(table_selector="   ").strip() == ""


def test_velora_chart_from_table_basic_attributes() -> None:
    out = _render_chart(table_selector="#t1", chart_type="bar", canvas_id="c1")
    assert 'data-velora-component="chart-from-table"' in out
    assert 'data-table-selector="#t1"' in out
    assert 'data-chart-type="bar"' in out
    assert 'id="c1"' in out
    assert "velora-chart" in out


def test_velora_chart_from_table_default_canvas_id() -> None:
    out = _render_chart(table_selector="#x")
    assert 'id="velora-chart-canvas"' in out


def test_velora_chart_from_table_invalid_type_falls_back() -> None:
    out = _render_chart(table_selector="#x", chart_type="donut")
    assert 'data-chart-type="line"' in out


def test_velora_chart_from_table_height_clamp() -> None:
    out = _render_chart(table_selector="#x", height=40)
    assert "height: 80px" in out  # min 80

    out2 = _render_chart(table_selector="#x", height=300)
    assert "height: 300px" in out2


def test_velora_chart_from_table_extra_class() -> None:
    out = _render_chart(table_selector="#x", extra_class="my-chart")
    assert "my-chart" in out
