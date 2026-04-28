"""Test per i nuovi link tag introdotti in v0.2 (Fase 10).

Coperti:
  - velora_settings_link        (10.9)
  - velora_toggle_link          (10.7)
  - velora_copy_link            (10.8)
  - velora_drop_down_link       (10.5)
  - velora_drop_down_button     (10.5)
  - velora_open_dialog_action_link (10.6)
"""

from __future__ import annotations

from django.template import Context, Template


def render(source: str, context: dict | None = None) -> str:
    return Template(source).render(Context(context or {}))


# -- velora_settings_link (10.9) ------------------------------------------


def test_settings_link_renders_with_green_class():
    html = render(
        "{% load velora_links %}{% velora_settings_link url='/cfg/' label='Configurazione' %}"
    )
    assert "velora-link-settings" in html
    assert 'href="/cfg/"' in html
    assert "Configurazione" in html


def test_settings_link_default_label():
    html = render("{% load velora_links %}{% velora_settings_link url='/cfg/' %}")
    assert "Impostazioni" in html


def test_settings_link_disabled():
    html = render(
        "{% load velora_links %}{% velora_settings_link url='/cfg/' disabled=True %}"
    )
    assert "is-disabled" in html
    assert 'aria-disabled="true"' in html
    assert 'href="#"' in html


# -- velora_toggle_link (10.7) --------------------------------------------


def test_toggle_link_renders_attrs_and_initial_label():
    html = render(
        "{% load velora_links %}{% velora_toggle_link target='#dettagli' label_show='Mostra' label_hide='Nascondi' %}"
    )
    assert 'data-velora-component="toggle-link"' in html
    assert 'data-toggle-target="#dettagli"' in html
    assert 'data-toggle-label-show="Mostra"' in html
    assert 'data-toggle-label-hide="Nascondi"' in html
    assert 'data-toggle-state="hidden"' in html
    assert ">Mostra</a>" in html


def test_toggle_link_initial_state_shown():
    html = render(
        "{% load velora_links %}{% velora_toggle_link target='#x' label_show='Mostra' label_hide='Nascondi' initial_state='shown' %}"
    )
    assert 'data-toggle-state="shown"' in html
    assert ">Nascondi</a>" in html
    assert "is-active" in html


def test_toggle_link_no_target_emits_nothing():
    html = render("{% load velora_links %}{% velora_toggle_link target='' %}")
    assert html.strip() == ""


# -- velora_copy_link (10.8) ----------------------------------------------


def test_copy_link_with_static_value():
    html = render(
        "{% load velora_links %}{% velora_copy_link value='abc-123' label='Copia ID' %}"
    )
    assert 'data-velora-component="copy-link"' in html
    assert 'data-copy-value="abc-123"' in html
    assert 'data-copy-target=""' in html
    assert 'data-copy-label="Copia ID"' in html
    assert 'data-copy-label-copied="Copiato"' in html
    assert ">Copia ID</a>" in html


def test_copy_link_with_target_selector():
    html = render(
        "{% load velora_links %}{% velora_copy_link target='#input-share' label='Copia link' label_copied='Fatto!' %}"
    )
    assert 'data-copy-target="#input-share"' in html
    assert 'data-copy-label-copied="Fatto!"' in html


def test_copy_link_neither_value_nor_target_emits_nothing():
    html = render("{% load velora_links %}{% velora_copy_link %}")
    assert html.strip() == ""


# -- velora_drop_down_link / velora_drop_down_button (10.5) ---------------


def test_drop_down_link_renders_panel_with_items():
    html = render(
        "{% load velora_links %}{% velora_drop_down_link label='Azioni' items=items %}",
        {
            "items": [
                {"label": "Modifica", "url": "/edit/"},
                {"label": "Elimina", "url": "/del/"},
            ]
        },
    )
    assert "velora-dropdown" in html
    assert 'data-velora-component="dropdown"' in html
    assert 'aria-haspopup="true"' in html
    assert 'aria-expanded="false"' in html
    assert "velora-link-dropdown" in html
    assert "Azioni" in html
    assert 'href="/edit/"' in html
    assert 'href="/del/"' in html
    assert html.count('role="menuitem"') == 2


def test_drop_down_link_align_right():
    html = render(
        "{% load velora_links %}{% velora_drop_down_link label='X' items=items align='right' %}",
        {"items": [{"label": "A", "url": "/a"}]},
    )
    assert 'data-velora-dropdown-align="right"' in html


def test_drop_down_link_align_invalid_falls_back_to_left():
    html = render(
        "{% load velora_links %}{% velora_drop_down_link label='X' items=items align='diag' %}",
        {"items": [{"label": "A", "url": "/a"}]},
    )
    assert 'data-velora-dropdown-align="left"' in html


def test_drop_down_link_filters_malformed_items():
    html = render(
        "{% load velora_links %}{% velora_drop_down_link label='X' items=items %}",
        {
            "items": [
                {"label": "Ok", "url": "/ok"},
                {"label": "Senza url"},
                "stringa",
                {"url": "/senza-label"},
            ]
        },
    )
    assert "Ok" in html
    assert "Senza url" not in html


def test_drop_down_link_empty_items_emits_nothing():
    html = render(
        "{% load velora_links %}{% velora_drop_down_link label='X' items=items %}",
        {"items": []},
    )
    assert html.strip() == ""


def test_drop_down_button_uses_btn_classes():
    html = render(
        "{% load velora_links %}{% velora_drop_down_button label='Salva' items=items variant='primary' %}",
        {"items": [{"label": "Standard", "url": "/s"}]},
    )
    assert "velora-btn velora-btn--primary" in html
    assert "Salva" in html


def test_drop_down_button_invalid_variant_falls_back_to_secondary():
    html = render(
        "{% load velora_links %}{% velora_drop_down_button label='X' items=items variant='ghost' %}",
        {"items": [{"label": "A", "url": "/a"}]},
    )
    assert "velora-btn--secondary" in html


# -- velora_open_dialog_action_link (10.6) --------------------------------


def test_open_dialog_action_link_inline_target():
    html = render(
        "{% load velora_links %}{% velora_open_dialog_action_link label='Modifica' target='#dialog-edit' %}"
    )
    assert 'data-velora-component="dialog"' in html
    assert 'data-dialog-target="#dialog-edit"' in html
    assert 'data-dialog-url=""' in html
    assert 'data-dialog-size="md"' in html
    assert 'href="#"' in html
    assert "Modifica" in html


def test_open_dialog_action_link_remote_url():
    html = render(
        "{% load velora_links %}{% velora_open_dialog_action_link label='Anteprima' url='/preview/42/' size='lg' dialog_title='Anteprima cliente' %}"
    )
    assert 'data-dialog-url="/preview/42/"' in html
    assert 'data-dialog-target=""' in html
    assert 'data-dialog-size="lg"' in html
    assert 'data-dialog-title="Anteprima cliente"' in html
    assert 'href="/preview/42/"' in html


def test_open_dialog_action_link_invalid_size_falls_back_to_md():
    html = render(
        "{% load velora_links %}{% velora_open_dialog_action_link label='X' target='#m' size='huge' %}"
    )
    assert 'data-dialog-size="md"' in html


def test_open_dialog_action_link_no_target_no_url_emits_nothing():
    html = render(
        "{% load velora_links %}{% velora_open_dialog_action_link label='X' %}"
    )
    assert html.strip() == ""
