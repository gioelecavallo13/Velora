"""Test del template tag library `velora_forms` (M3 - Fase 5 del piano).

Coperto:
  - velora_form_row su tutti i 7 tipi v0.1: text, textarea, select, checkbox,
    radio, onoff, file (rendering del control + label + required + value)
  - velora_form_row: validazione argomenti (name obbligatorio, type sconosciuto)
  - velora_form_row: stato error (modificatore --error sul wrapper)
  - velora_form_row text: input_type fra i validi e fallback a "text"
  - velora_search_box: render del form e bottone submit
  - velora_fields_separator: con e senza label, modificatore --plain
  - widgets.OnOffWidget: rendering tramite form Django nativo
"""

from __future__ import annotations

import pytest
from django.template import Context, Template, TemplateSyntaxError


def render(source: str, context: dict | None = None) -> str:
    return Template(source).render(Context(context or {}))


# -- velora_form_row: validazione --------------------------------------


def test_form_row_requires_name():
    with pytest.raises(TemplateSyntaxError):
        render("{% load velora_forms %}{% velora_form_row type='text' %}")


def test_form_row_rejects_unknown_type():
    with pytest.raises(TemplateSyntaxError):
        render(
            "{% load velora_forms %}{% velora_form_row type='magic' name='x' %}"
        )


# -- type=text ----------------------------------------------------------


def test_form_row_text_basic():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='text' name='email' label='Email' value='a@b.com' required=True %}"
    )
    assert 'type="text"' in html
    assert 'name="email"' in html
    assert 'value="a@b.com"' in html
    assert "required" in html
    assert "Email" in html
    assert "velora-form-row--text" in html


def test_form_row_text_input_type_email_kept():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='text' name='m' input_type='email' %}"
    )
    assert 'type="email"' in html


def test_form_row_text_input_type_unknown_falls_back_to_text():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='text' name='m' input_type='alien' %}"
    )
    assert 'type="text"' in html


def test_form_row_text_id_default():
    html = render(
        "{% load velora_forms %}{% velora_form_row type='text' name='foo' %}"
    )
    assert 'id="id_foo"' in html


def test_form_row_text_id_override():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='text' name='foo' id='custom-id' %}"
    )
    assert 'id="custom-id"' in html
    assert 'id="id_foo"' not in html


def test_form_row_text_default_label_capitalizes_name():
    html = render(
        "{% load velora_forms %}{% velora_form_row type='text' name='first_name' %}"
    )
    assert "First name" in html


def test_form_row_text_error_state():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='text' name='m' error='campo errato' %}"
    )
    assert "velora-form-row--error" in html
    assert "campo errato" in html


def test_form_row_text_help_text():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='text' name='m' help_text='inserisci email aziendale' %}"
    )
    assert "inserisci email aziendale" in html
    assert "velora-form-row__help" in html


# -- type=textarea ------------------------------------------------------


def test_form_row_textarea_basic():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='textarea' name='note' rows=8 value='ciao' %}"
    )
    assert "<textarea" in html
    assert 'rows="8"' in html
    assert ">ciao</textarea>" in html


# -- type=select --------------------------------------------------------


def test_form_row_select_renders_choices():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='select' name='c' choices=choices value='b' %}",
        {"choices": [("a", "Alpha"), ("b", "Beta"), ("c", "Charlie")]},
    )
    assert '<option\n            value="a"' in html or 'value="a"' in html
    assert "Alpha" in html
    assert "Beta" in html
    # Solo la option "b" deve avere selected
    assert html.count("selected") == 1


def test_form_row_select_empty_label():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='select' name='c' choices=choices empty_label='-- scegli --' %}",
        {"choices": [("a", "Alpha")]},
    )
    assert '<option value="">-- scegli --</option>' in html


def test_form_row_select_choices_as_dicts():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='select' name='c' choices=choices %}",
        {"choices": [{"value": "x", "label": "Iks", "disabled": True}]},
    )
    assert "Iks" in html
    assert "disabled" in html


# -- type=checkbox ------------------------------------------------------


def test_form_row_checkbox_unchecked():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='checkbox' name='ok' label='Accetto' %}"
    )
    assert 'type="checkbox"' in html
    assert "Accetto" in html
    assert "checked" not in html


def test_form_row_checkbox_checked_when_value_truthy():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='checkbox' name='ok' value=True %}"
    )
    assert "checked" in html


# -- type=radio ---------------------------------------------------------


def test_form_row_radio_renders_group():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='radio' name='size' choices=choices value='m' %}",
        {"choices": [("s", "Small"), ("m", "Medium"), ("l", "Large")]},
    )
    # tre input radio condividono lo stesso name
    assert html.count('name="size"') == 3
    # solo "m" e` checked
    assert html.count("checked") == 1
    assert "Medium" in html


# -- type=onoff ---------------------------------------------------------


def test_form_row_onoff_off_by_default():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='onoff' name='enabled' label='Notifiche' %}"
    )
    assert "velora-form-row__onoff" in html
    assert 'type="checkbox"' in html
    assert "checked" not in html
    assert "Notifiche" in html


def test_form_row_onoff_on_when_value_truthy():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='onoff' name='enabled' value=True %}"
    )
    assert "checked" in html


def test_form_row_onoff_custom_value_on():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='onoff' name='enabled' value=True value_on='yes' %}"
    )
    assert 'value="yes"' in html


# -- type=file ----------------------------------------------------------


def test_form_row_file_basic():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='file' name='avatar' accept='image/*' %}"
    )
    assert 'type="file"' in html
    assert 'name="avatar"' in html
    assert 'accept="image/*"' in html


def test_form_row_file_multiple_appends_brackets():
    html = render(
        "{% load velora_forms %}"
        "{% velora_form_row type='file' name='docs' multiple=True %}"
    )
    assert 'name="docs[]"' in html
    assert "multiple" in html


# -- velora_search_box --------------------------------------------------


def test_search_box_renders_form_with_input_and_submit():
    html = render(
        "{% load velora_forms %}{% velora_search_box %}"
    )
    assert "<form" in html
    assert 'role="search"' in html
    assert 'type="search"' in html
    assert 'name="q"' in html
    assert "<button" in html


def test_search_box_method_lowercased():
    html = render(
        "{% load velora_forms %}{% velora_search_box method='POST' %}"
    )
    assert 'method="post"' in html


def test_search_box_action_emitted():
    html = render(
        "{% load velora_forms %}{% velora_search_box action='/search/' %}"
    )
    assert 'action="/search/"' in html


# -- velora_fields_separator -------------------------------------------


def test_fields_separator_with_label():
    html = render(
        "{% load velora_forms %}{% velora_fields_separator label='oppure' %}"
    )
    assert "oppure" in html
    assert "velora-fields-separator" in html
    assert "velora-fields-separator--plain" not in html


def test_fields_separator_plain_modifier_when_no_label():
    html = render(
        "{% load velora_forms %}{% velora_fields_separator %}"
    )
    assert "velora-fields-separator--plain" in html


# -- OnOffWidget --------------------------------------------------------


def test_onoff_widget_renders_via_django_form():
    """OnOffWidget deve produrre il markup velora-form-row__onoff* anche
    quando usato da una form Django nativa (non dal nostro template tag).
    """
    from django import forms

    from velora_ui.widgets import OnOffWidget

    class _F(forms.Form):
        notifications = forms.BooleanField(
            required=False, widget=OnOffWidget()
        )

    rendered = str(_F()["notifications"])
    assert "velora-form-row__onoff-input" in rendered
    assert "velora-form-row__onoff-track" in rendered
    assert 'type="checkbox"' in rendered


def test_onoff_widget_value_on_default_is_1():
    from django import forms

    from velora_ui.widgets import OnOffWidget

    class _F(forms.Form):
        x = forms.BooleanField(required=False, widget=OnOffWidget())

    rendered = str(_F()["x"])
    assert 'value="1"' in rendered


def test_onoff_widget_custom_value_on():
    from django import forms

    from velora_ui.widgets import OnOffWidget

    class _F(forms.Form):
        x = forms.BooleanField(required=False, widget=OnOffWidget(value_on="yes"))

    rendered = str(_F()["x"])
    assert 'value="yes"' in rendered
