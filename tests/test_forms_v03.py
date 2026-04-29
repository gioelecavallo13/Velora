"""Test dei nuovi field_type di `velora_form_row` (Fase 11 — v0.3.0).

Coperti i 9 nuovi tipi:
  - datepicker / datetimepicker
  - multiselect
  - autocomplete (locale) / remote_autocomplete (AJAX)
  - image_preview
  - rating_stars
  - timer_fields
  - redactor

Inoltre testa `velora_checkbox_tag` con varianti colore.

I test verificano: render base, normalizzazione input, fallback su valori
invalidi, attributi data-* presenti, comportamento di scarto su input vuoti.
"""

from __future__ import annotations

import json

import pytest
from django.template import Context, Template, TemplateSyntaxError


def render(source: str, ctx: dict | None = None) -> str:
    return Template(source).render(Context(ctx or {}))


LOAD = "{% load velora_forms %}"


# -- datepicker -----------------------------------------------------------


def test_datepicker_basic() -> None:
    out = render(LOAD + '{% velora_form_row type="datepicker" name="dob" label="Nascita" %}')
    assert "velora-form-row--datepicker" in out
    assert 'name="dob"' in out
    assert 'data-velora-component="datepicker"' in out
    assert 'data-format="YYYY-MM-DD"' in out
    assert 'data-first-day="1"' in out


def test_datepicker_with_min_max_format() -> None:
    out = render(
        LOAD
        + '{% velora_form_row type="datepicker" name="d" min="2024-01-01" '
        + 'max="2025-12-31" first_day=0 format="DD/MM/YYYY" %}'
    )
    assert 'data-min="2024-01-01"' in out
    assert 'data-max="2025-12-31"' in out
    assert 'data-first-day="0"' in out
    assert 'data-format="DD/MM/YYYY"' in out


def test_datepicker_first_day_invalid_falls_back_to_1() -> None:
    out = render(LOAD + '{% velora_form_row type="datepicker" name="d" first_day="abc" %}')
    assert 'data-first-day="1"' in out


# -- datetimepicker -------------------------------------------------------


def test_datetimepicker_data_time_attr() -> None:
    out = render(LOAD + '{% velora_form_row type="datetimepicker" name="when" %}')
    assert 'data-time="true"' in out
    assert 'data-time-format="HH:mm"' in out
    assert 'data-step-minutes="5"' in out


def test_datetimepicker_step_custom() -> None:
    out = render(
        LOAD
        + '{% velora_form_row type="datetimepicker" name="when" step_minutes=15 %}'
    )
    assert 'data-step-minutes="15"' in out


# -- multiselect ----------------------------------------------------------


def test_multiselect_render_options_with_selection() -> None:
    out = render(
        LOAD
        + '{% velora_form_row type="multiselect" name="tags" choices=choices value=value %}',
        {
            "choices": [
                {"value": "a", "label": "Alpha"},
                {"value": "b", "label": "Beta"},
                {"value": "c", "label": "Gamma"},
            ],
            "value": ["a", "c"],
        },
    )
    assert "velora-multiselect" in out
    assert 'multiple' in out
    assert 'value="a"' in out and "selected" in out  # opt selezionata
    assert 'value="b"' in out  # opt non selezionata
    # "Beta" non deve avere selected
    beta_idx = out.find('value="b"')
    assert beta_idx > 0
    assert 'selected' not in out[beta_idx : beta_idx + 60]


def test_multiselect_value_csv_string() -> None:
    out = render(
        LOAD
        + '{% velora_form_row type="multiselect" name="t" choices=choices value="a,c" %}',
        {"choices": [("a", "A"), ("b", "B"), ("c", "C")]},
    )
    # Due opzioni selezionate (a, c)
    assert out.count("selected") == 2


def test_multiselect_empty_choices() -> None:
    out = render(LOAD + '{% velora_form_row type="multiselect" name="t" %}')
    assert "velora-multiselect" in out
    assert "<option" not in out


# -- autocomplete ---------------------------------------------------------


def test_autocomplete_local_options_json() -> None:
    out = render(
        LOAD + '{% velora_form_row type="autocomplete" name="city" options=opts %}',
        {"opts": [{"value": "rm", "label": "Roma"}, {"value": "mi", "label": "Milano"}]},
    )
    assert 'data-velora-component="autocomplete"' in out
    # Lo script con i dati JSON
    assert '<script type="application/json"' in out
    # Estrazione del JSON
    import re
    m = re.search(r'<script[^>]*velora-autocomplete__data[^>]*>(.+?)</script>', out)
    assert m, out
    data = json.loads(m.group(1))
    assert data == [{"value": "rm", "label": "Roma"}, {"value": "mi", "label": "Milano"}]


def test_autocomplete_filter_empty_label() -> None:
    out = render(
        LOAD + '{% velora_form_row type="autocomplete" name="x" options=opts %}',
        {"opts": [{"value": "1", "label": ""}, {"value": "2", "label": "OK"}]},
    )
    import re
    data = json.loads(re.search(r'data">(.+?)</script>', out).group(1))
    assert data == [{"value": "2", "label": "OK"}]


def test_autocomplete_min_chars_default() -> None:
    out = render(LOAD + '{% velora_form_row type="autocomplete" name="x" %}')
    assert 'data-min-chars="1"' in out


# -- remote_autocomplete --------------------------------------------------


def test_remote_autocomplete_basic() -> None:
    out = render(
        LOAD
        + '{% velora_form_row type="remote_autocomplete" name="user" url="/api/users/" %}'
    )
    assert 'data-remote-url="/api/users/"' in out
    assert 'data-query-param="q"' in out
    assert 'data-min-chars="2"' in out
    assert 'data-debounce-ms="300"' in out
    assert 'data-limit="10"' in out
    # Hidden input + visible label input
    assert 'name="user"' in out and 'type="hidden"' in out
    assert 'name="user_label"' in out


def test_remote_autocomplete_required_url() -> None:
    with pytest.raises(TemplateSyntaxError):
        render(LOAD + '{% velora_form_row type="remote_autocomplete" name="x" %}')


def test_remote_autocomplete_value_label_pre_populated() -> None:
    out = render(
        LOAD
        + '{% velora_form_row type="remote_autocomplete" name="u" url="/x" '
        + 'value=42 value_label="Mario Rossi" %}'
    )
    assert 'value="42"' in out  # nello hidden
    assert 'value="Mario Rossi"' in out  # nel visible


def test_remote_autocomplete_custom_params() -> None:
    out = render(
        LOAD
        + '{% velora_form_row type="remote_autocomplete" name="u" url="/x" '
        + 'query_param="search" min_chars=3 debounce_ms=500 limit=20 %}'
    )
    assert 'data-query-param="search"' in out
    assert 'data-min-chars="3"' in out
    assert 'data-debounce-ms="500"' in out
    assert 'data-limit="20"' in out


# -- image_preview --------------------------------------------------------


def test_image_preview_basic() -> None:
    out = render(LOAD + '{% velora_form_row type="image_preview" name="avatar" %}')
    assert 'velora-image-preview' in out
    assert 'type="file"' in out
    assert 'accept="image/*"' in out
    assert 'is-empty' in out  # senza value -> placeholder


def test_image_preview_with_initial_value() -> None:
    out = render(
        LOAD
        + '{% velora_form_row type="image_preview" name="a" value="/media/x.png" '
        + 'alt="Foto" %}'
    )
    assert 'src="/media/x.png"' in out
    assert 'alt="Foto"' in out
    assert "is-empty" not in out
    # Bottone clear presente di default (clearable=True)
    assert "data-clear" in out


def test_image_preview_clearable_false() -> None:
    out = render(
        LOAD
        + '{% velora_form_row type="image_preview" name="a" value="/x.png" clearable=False %}'
    )
    assert "data-clear" not in out


def test_image_preview_max_size_kb() -> None:
    out = render(
        LOAD + '{% velora_form_row type="image_preview" name="a" max_size_kb=500 %}'
    )
    assert 'data-max-size-kb="500"' in out


# -- rating_stars ---------------------------------------------------------


def test_rating_stars_default_5() -> None:
    out = render(LOAD + '{% velora_form_row type="rating_stars" name="r" %}')
    # 5 input radio (uno per stella)
    assert out.count('type="radio"') == 5
    # Ordine inverso: il primo nel HTML deve essere value=5
    first_radio = out.find('type="radio"')
    block = out[first_radio : first_radio + 200]
    assert 'value="5"' in block


def test_rating_stars_with_current_value() -> None:
    out = render(
        LOAD + '{% velora_form_row type="rating_stars" name="r" value=3 %}'
    )
    # Solo la stella value=3 deve avere checked
    assert out.count("checked") == 1
    # Cerco la riga con value="3" e checked
    import re
    m = re.search(r'value="3"\s+checked', out)
    assert m


def test_rating_stars_max_value_clamped() -> None:
    out = render(LOAD + '{% velora_form_row type="rating_stars" name="r" max_value=15 %}')
    # max_value > 10 -> clamp a 10
    assert out.count('type="radio"') == 10


def test_rating_stars_max_value_zero_falls_back_to_5() -> None:
    out = render(LOAD + '{% velora_form_row type="rating_stars" name="r" max_value=0 %}')
    assert out.count('type="radio"') == 5


# -- timer_fields ---------------------------------------------------------


def test_timer_fields_default_h_m_s() -> None:
    out = render(LOAD + '{% velora_form_row type="timer_fields" name="dur" %}')
    # 3 sub-input numerici (h, m, s) + 1 hidden = 4 input
    assert out.count('type="number"') == 3
    assert out.count('type="hidden"') == 1
    # Suffissi
    assert "ore" in out and "min" in out and "sec" in out


def test_timer_fields_custom_units() -> None:
    out = render(
        LOAD
        + '{% velora_form_row type="timer_fields" name="dur" units="d,h,m" %}'
    )
    assert out.count('type="number"') == 3
    assert "giorni" in out and "ore" in out
    # Il suffisso "sec" non deve comparire come label di unita`. Cerco solo
    # all'interno dei tag <span class="velora-timer__suffix">...</span> per
    # evitare falsi positivi (data-seconds contiene "sec").
    import re
    suffixes = re.findall(r'velora-timer__suffix">([^<]+)</span>', out)
    assert "sec" not in suffixes
    assert "min" in suffixes


def test_timer_fields_value_distribution() -> None:
    # 1 ora 30 min 15 sec = 5415 secondi
    out = render(
        LOAD
        + '{% velora_form_row type="timer_fields" name="dur" value=5415 %}'
    )
    # I sub-input devono essere 1, 30, 15 (in ordine ore, min, sec)
    import re
    fields = re.findall(r'data-unit="(\w+)"\s+data-seconds="\d+"\s+value="(\d+)"', out)
    by_unit = dict(fields)
    assert by_unit["h"] == "1"
    assert by_unit["m"] == "30"
    assert by_unit["s"] == "15"
    # Hidden contiene il totale originale
    assert 'value="5415"' in out


def test_timer_fields_value_invalid_string_zero() -> None:
    out = render(
        LOAD
        + '{% velora_form_row type="timer_fields" name="dur" value="abc" %}'
    )
    # Tutti i sub-input a 0
    import re
    fields = re.findall(r'data-unit="\w+"\s+data-seconds="\d+"\s+value="(\d+)"', out)
    assert all(v == "0" for v in fields)


def test_timer_fields_unknown_unit_ignored_fallback() -> None:
    # Tutte unita` sconosciute -> fallback h,m,s
    out = render(
        LOAD + '{% velora_form_row type="timer_fields" name="dur" units="zz,kk" %}'
    )
    assert out.count('type="number"') == 3
    assert "ore" in out


# -- redactor -------------------------------------------------------------


def test_redactor_basic() -> None:
    out = render(LOAD + '{% velora_form_row type="redactor" name="body" %}')
    assert 'data-velora-component="redactor"' in out
    assert "<textarea" in out
    assert 'rows="8"' in out


def test_redactor_value_in_textarea() -> None:
    out = render(
        LOAD + '{% velora_form_row type="redactor" name="b" value=val %}',
        {"val": "<p>ciao</p>"},
    )
    # Django auto-escape sulla textarea
    assert "&lt;p&gt;ciao&lt;/p&gt;" in out


def test_redactor_custom_rows_toolbar() -> None:
    out = render(
        LOAD
        + '{% velora_form_row type="redactor" name="b" rows=12 toolbar="minimal" %}'
    )
    assert 'rows="12"' in out
    assert 'data-toolbar="minimal"' in out


# -- velora_checkbox_tag (Fase 11.12) -------------------------------------


def test_checkbox_tag_basic() -> None:
    out = render(LOAD + '{% velora_checkbox_tag name="agree" label="Accetto" %}')
    assert "velora-checkbox" in out
    assert 'type="checkbox"' in out
    assert 'name="agree"' in out
    assert "Accetto" in out
    assert "velora-checkbox--default" in out
    assert "velora-checkbox--align-left" in out


def test_checkbox_tag_no_name_emits_empty() -> None:
    out = render(LOAD + '{% velora_checkbox_tag label="X" %}')
    # Skipped silently
    assert "velora-checkbox" not in out
    assert "<label" not in out


def test_checkbox_tag_radio_mode() -> None:
    out = render(
        LOAD
        + '{% velora_checkbox_tag name="role" label="Admin" value="admin" radio=True variant="primary" %}'
    )
    assert 'type="radio"' in out
    assert 'value="admin"' in out
    assert "velora-checkbox--primary" in out
    # id deve includere lo slug del value per consentire group
    assert 'id="id_role_admin"' in out


def test_checkbox_tag_variant_invalid_falls_back_to_default() -> None:
    out = render(
        LOAD + '{% velora_checkbox_tag name="x" variant="weirdvariant" %}'
    )
    assert "velora-checkbox--default" in out
    assert "velora-checkbox--weirdvariant" not in out


def test_checkbox_tag_align_right() -> None:
    out = render(LOAD + '{% velora_checkbox_tag name="x" align="right" %}')
    assert "velora-checkbox--align-right" in out


def test_checkbox_tag_checked_disabled() -> None:
    out = render(
        LOAD
        + '{% velora_checkbox_tag name="x" checked=True disabled=True variant="success" %}'
    )
    assert "checked" in out
    assert "disabled" in out
    assert "is-disabled" in out
    assert "velora-checkbox--success" in out


def test_checkbox_tag_all_variants() -> None:
    for variant in ("default", "primary", "info", "success", "danger"):
        out = render(
            LOAD + '{% velora_checkbox_tag name="x" variant="' + variant + '" %}'
        )
        assert f"velora-checkbox--{variant}" in out
