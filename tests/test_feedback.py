"""Test per `velora_feedback` (M5 - Fase 7 del piano).

Coperto:
  - velora_alert: 4 varianti, fallback a info su variant invalida,
    dismissible, title opzionale, escape XSS sul message.
  - velora_label: 5 varianti, fallback a neutral, escape sul text.
  - velora_toast_messages: render dei messaggi del framework Django
    `messages` come <script type="application/json"> con mappatura dei
    livelli; storage marcato come "used" dopo il rendering; html vuoto
    se non ci sono messaggi o non c'e` request nel contesto.
"""

from __future__ import annotations

import json
import re

import pytest
from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.template import Context, Template
from django.test import RequestFactory


def render(source: str, context: dict | None = None) -> str:
    return Template(source).render(Context(context or {}))


# -- velora_alert ------------------------------------------------------


@pytest.mark.parametrize(
    "variant",
    ["success", "error", "warning", "info"],
)
def test_alert_renders_each_variant(variant):
    html = render(
        "{% load velora_feedback %}{% velora_alert variant=v message='ok' %}",
        {"v": variant},
    )
    assert f"velora-alert--{variant}" in html
    assert "ok" in html
    assert 'role="alert"' in html


def test_alert_unknown_variant_falls_back_to_info():
    html = render(
        "{% load velora_feedback %}{% velora_alert variant='alien' message='ok' %}"
    )
    assert "velora-alert--info" in html
    assert "velora-alert--alien" not in html


def test_alert_dismissible_emits_close_button():
    html = render(
        "{% load velora_feedback %}"
        "{% velora_alert variant='success' message='x' dismissible=True %}"
    )
    assert "velora-alert__close" in html
    assert 'aria-label="Chiudi"' in html


def test_alert_default_is_not_dismissible():
    html = render(
        "{% load velora_feedback %}{% velora_alert variant='info' message='x' %}"
    )
    assert "velora-alert__close" not in html


def test_alert_title_optional():
    html = render(
        "{% load velora_feedback %}"
        "{% velora_alert variant='warning' title='Attento' message='x' %}"
    )
    assert "velora-alert__title" in html
    assert "Attento" in html


def test_alert_escapes_message():
    html = render(
        "{% load velora_feedback %}{% velora_alert variant='info' message=m %}",
        {"m": "<img src=x onerror=alert(1)>"},
    )
    assert "<img src=x" not in html
    assert "&lt;img" in html


# -- velora_label ------------------------------------------------------


@pytest.mark.parametrize(
    "variant", ["success", "error", "warning", "info", "neutral"]
)
def test_label_renders_each_variant(variant):
    html = render(
        "{% load velora_feedback %}{% velora_label variant=v text='Stato' %}",
        {"v": variant},
    )
    assert f"velora-label--{variant}" in html
    assert "Stato" in html


def test_label_unknown_variant_falls_back_to_neutral():
    html = render(
        "{% load velora_feedback %}{% velora_label variant='alien' text='X' %}"
    )
    assert "velora-label--neutral" in html


def test_label_escapes_text():
    html = render(
        "{% load velora_feedback %}{% velora_label variant='info' text=t %}",
        {"t": "<b>Hack</b>"},
    )
    assert "<b>Hack</b>" not in html
    assert "&lt;b&gt;Hack" in html


# -- velora_toast_messages ---------------------------------------------


def _request_with_messages():
    """Crea una request con un FallbackStorage attivo per i `messages`."""

    rf = RequestFactory()
    request = rf.get("/")
    setattr(request, "session", {})
    setattr(request, "_messages", FallbackStorage(request))
    return request


def _extract_payloads(html: str) -> list[dict]:
    """Estrae i dict JSON dai blocchi <script data-velora-toast>."""

    pattern = re.compile(
        r'<script type="application/json" data-velora-toast>(.*?)</script>',
        re.DOTALL,
    )
    return [json.loads(m.group(1)) for m in pattern.finditer(html)]


def test_toast_messages_renders_for_each_message():
    request = _request_with_messages()
    messages.success(request, "Tutto ok")
    messages.error(request, "Esplosione")
    messages.warning(request, "Occhio")
    messages.info(request, "Dettaglio")

    html = render(
        "{% load velora_feedback %}{% velora_toast_messages %}",
        {"request": request},
    )
    payloads = _extract_payloads(html)
    assert [p["variant"] for p in payloads] == ["success", "error", "warning", "info"]
    assert [p["message"] for p in payloads] == [
        "Tutto ok",
        "Esplosione",
        "Occhio",
        "Dettaglio",
    ]


def test_toast_messages_maps_debug_to_info():
    request = _request_with_messages()
    # DEBUG e` filtrato da Django se MESSAGE_LEVEL > DEBUG (default INFO):
    # abbassiamo la soglia per questo specifico test.
    messages.set_level(request, messages.DEBUG)
    messages.debug(request, "dbg")
    html = render(
        "{% load velora_feedback %}{% velora_toast_messages %}",
        {"request": request},
    )
    payloads = _extract_payloads(html)
    assert payloads == [{"variant": "info", "message": "dbg", "tags": ""}]


def test_toast_messages_passes_extra_tags():
    request = _request_with_messages()
    messages.success(request, "Salvato", extra_tags="persistent flash")
    html = render(
        "{% load velora_feedback %}{% velora_toast_messages %}",
        {"request": request},
    )
    payloads = _extract_payloads(html)
    assert payloads[0]["tags"] == "persistent flash"


def test_toast_messages_empty_when_no_messages():
    request = _request_with_messages()
    html = render(
        "{% load velora_feedback %}{% velora_toast_messages %}",
        {"request": request},
    )
    assert "data-velora-toast" not in html


def test_toast_messages_safe_when_no_request():
    html = render(
        "{% load velora_feedback %}{% velora_toast_messages %}",
        {},
    )
    # Nessuna eccezione, output vuoto
    assert "data-velora-toast" not in html


def test_toast_messages_escapes_close_script_breakout():
    """Un messaggio contenente '</script>' non deve far chiudere il
    blocco JSON inline."""

    request = _request_with_messages()
    messages.success(request, "</script><b>boom</b>")
    html = render(
        "{% load velora_feedback %}{% velora_toast_messages %}",
        {"request": request},
    )
    # Il payload e` ancora dentro un solo <script> chiuso correttamente
    assert html.count("<script") == 1
    assert html.count("</script>") == 1
    # E il contenuto e` stato escapato in modo che JSON.parse lo recuperi
    assert "<\\/script>" in html


def test_toast_messages_marks_storage_used():
    """`storage.used = True` non svuota lo storage in-memory ma serve al
    middleware Django per cancellare cookie/session a fine request, cosi`
    i messaggi non si propagano alla pagina successiva.
    """

    request = _request_with_messages()
    messages.success(request, "x")
    storage = request._messages
    assert storage.used is False

    render(
        "{% load velora_feedback %}{% velora_toast_messages %}",
        {"request": request},
    )
    assert storage.used is True
