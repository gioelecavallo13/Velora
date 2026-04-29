"""Test estensioni v0.3 di `velora_table` + `velora_select_all_table_rows`.

Coperti:
  - velora_table: form-in-cell schema (text/select/checkbox/onoff)
  - velora_table: scarto silenzioso di form_in_cell malformato
  - velora_table: opzione `selectable=True` aggiunge colonna checkbox
  - velora_select_all_table_rows: rendering toolbar
  - velora_select_all_table_rows: bulk_actions normalization
  - velora_select_all_table_rows: target vuoto -> tag emette stringa vuota
"""

from __future__ import annotations

from django.template import Context, Template
from django.utils.safestring import mark_safe


def render(source: str, ctx: dict | None = None) -> str:
    return Template(source).render(Context(ctx or {}))


LOAD = "{% load velora_data %}"


# -- form-in-cell ---------------------------------------------------------


def test_table_form_in_cell_text_renders_input() -> None:
    out = render(
        LOAD + "{% velora_table headers=h rows=r %}",
        {
            "h": [{"key": "name", "label": "Nome"}, {"key": "edit", "label": "Edita"}],
            "r": [
                {
                    "name": "Mario",
                    "edit": {
                        "value": "Mario",
                        "form_in_cell": {
                            "type": "text",
                            "name": "fullname",
                            "value": "Mario",
                            "url": "/api/u/1/",
                            "row_id": 1,
                        },
                    },
                }
            ],
        },
    )
    assert "velora-cell-form" in out
    assert 'data-fic-type="text"' in out
    assert 'data-fic-url="/api/u/1/"' in out
    assert 'data-fic-method="patch"' in out
    assert 'data-fic-row-id="1"' in out
    assert 'name="fullname"' in out
    assert 'value="Mario"' in out


def test_table_form_in_cell_select_renders_options() -> None:
    out = render(
        LOAD + "{% velora_table headers=h rows=r %}",
        {
            "h": [{"key": "role", "label": "Ruolo"}],
            "r": [
                {
                    "role": {
                        "value": "Admin",
                        "form_in_cell": {
                            "type": "select",
                            "name": "role",
                            "value": "admin",
                            "url": "/api/u/1/",
                            "choices": [("admin", "Admin"), ("user", "User")],
                        },
                    }
                }
            ],
        },
    )
    assert "<select" in out
    assert 'value="admin"' in out
    assert 'value="user"' in out
    assert "selected" in out  # admin selezionata


def test_table_form_in_cell_onoff_renders_button() -> None:
    out = render(
        LOAD + "{% velora_table headers=h rows=r %}",
        {
            "h": [{"key": "active", "label": "Attivo"}],
            "r": [
                {
                    "active": {
                        "value": True,
                        "form_in_cell": {
                            "type": "onoff",
                            "name": "active",
                            "value": True,
                            "url": "/api/u/1/",
                        },
                    }
                }
            ],
        },
    )
    assert "velora-cell-form__onoff" in out
    assert "is-on" in out
    assert 'aria-checked="true"' in out


def test_table_form_in_cell_missing_url_falls_back_to_value() -> None:
    """Se form_in_cell ha schema incompleto, la cella renderizza solo `value`."""
    out = render(
        LOAD + "{% velora_table headers=h rows=r %}",
        {
            "h": [{"key": "x", "label": "X"}],
            "r": [
                {
                    "x": {
                        "value": "fallback-text",
                        "form_in_cell": {"type": "text", "name": "x"},  # no url
                    }
                }
            ],
        },
    )
    assert "velora-cell-form" not in out
    assert "fallback-text" in out


def test_table_form_in_cell_unknown_type_skipped() -> None:
    out = render(
        LOAD + "{% velora_table headers=h rows=r %}",
        {
            "h": [{"key": "x", "label": "X"}],
            "r": [
                {
                    "x": {
                        "value": "raw-only",
                        "form_in_cell": {
                            "type": "fancytype",
                            "name": "x",
                            "url": "/x/",
                        },
                    }
                }
            ],
        },
    )
    assert "velora-cell-form" not in out
    assert "raw-only" in out


def test_table_form_in_cell_invalid_method_falls_back_to_patch() -> None:
    out = render(
        LOAD + "{% velora_table headers=h rows=r %}",
        {
            "h": [{"key": "x", "label": "X"}],
            "r": [
                {
                    "x": {
                        "value": "v",
                        "form_in_cell": {
                            "type": "text",
                            "name": "x",
                            "url": "/x/",
                            "method": "weird",
                        },
                    }
                }
            ],
        },
    )
    assert 'data-fic-method="patch"' in out


# -- selectable + select_all ---------------------------------------------


def test_table_selectable_adds_checkbox_column() -> None:
    out = render(
        LOAD + "{% velora_table headers=h rows=r selectable=True %}",
        {
            "h": [{"key": "name", "label": "Nome"}],
            "r": [{"id": 1, "name": "Mario"}, {"id": 2, "name": "Luca"}],
        },
    )
    assert "velora-table--selectable" in out
    assert "velora-table__select-master" in out
    # Una checkbox di riga per ogni row
    assert out.count("velora-table__select-row") == 2
    # row_ids rendered come data-row-id
    assert 'data-row-id="1"' in out
    assert 'data-row-id="2"' in out


def test_table_selectable_custom_row_id_key() -> None:
    out = render(
        LOAD + '{% velora_table headers=h rows=r selectable=True row_id_key="uuid" %}',
        {
            "h": [{"key": "name", "label": "Nome"}],
            "r": [{"uuid": "abc-123", "name": "Mario"}],
        },
    )
    assert 'data-row-id="abc-123"' in out


def test_table_selectable_false_default() -> None:
    out = render(
        LOAD + "{% velora_table headers=h rows=r %}",
        {
            "h": [{"key": "name", "label": "Nome"}],
            "r": [{"id": 1, "name": "Mario"}],
        },
    )
    assert "velora-table--selectable" not in out
    assert "velora-table__select-row" not in out


def test_select_all_table_rows_basic() -> None:
    out = render(
        LOAD
        + '{% velora_select_all_table_rows target="#t1" url="/api/bulk/" actions=actions %}',
        {
            "actions": [
                {"label": "Elimina", "value": "delete", "variant": "danger", "confirm": "Sicuro?"},
                {"label": "Archivia", "value": "archive"},
            ],
        },
    )
    assert 'data-velora-component="select-all-table"' in out
    assert 'data-target="#t1"' in out
    assert 'data-url="/api/bulk/"' in out
    assert "Elimina" in out and "Archivia" in out
    assert 'data-action="delete"' in out
    assert 'data-confirm="Sicuro?"' in out
    assert "velora-btn--danger" in out
    assert "velora-btn--secondary" in out  # default per archive


def test_select_all_table_rows_target_empty_emits_nothing() -> None:
    out = render(LOAD + '{% velora_select_all_table_rows target="" %}')
    assert out.strip() == ""


def test_select_all_table_rows_filters_malformed_actions() -> None:
    out = render(
        LOAD + '{% velora_select_all_table_rows target="#t" actions=actions %}',
        {
            "actions": [
                {"label": "OK", "value": "ok"},
                {"label": "no value"},  # scartato
                {"value": "no_label"},  # scartato
                "not-a-dict",  # scartato
            ],
        },
    )
    assert "OK" in out
    assert "no value" not in out
    assert "no_label" not in out


def test_select_all_table_rows_invalid_method_falls_back() -> None:
    out = render(
        LOAD + '{% velora_select_all_table_rows target="#t" actions=actions %}',
        {"actions": [{"label": "X", "value": "x", "method": "weird"}]},
    )
    assert 'data-method="post"' in out


def test_select_all_table_rows_invalid_variant_falls_back() -> None:
    out = render(
        LOAD + '{% velora_select_all_table_rows target="#t" actions=actions %}',
        {"actions": [{"label": "X", "value": "x", "variant": "weird"}]},
    )
    assert "velora-btn--secondary" in out


def test_select_all_table_rows_default_label() -> None:
    out = render(LOAD + '{% velora_select_all_table_rows target="#t" %}')
    assert "Selezionati" in out


def test_select_all_table_rows_custom_name() -> None:
    out = render(
        LOAD + '{% velora_select_all_table_rows target="#t" name="user_ids" %}'
    )
    assert 'data-name="user_ids"' in out
