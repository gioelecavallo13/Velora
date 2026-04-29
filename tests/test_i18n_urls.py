"""Smoke test URL i18n (Fase 12.6)."""

from __future__ import annotations

from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from django.urls import reverse
from django.utils import translation

from showcase.views import index


def test_set_language_url_reverse() -> None:
    assert reverse("set_language") == "/i18n/setlang/"


def _request_with_message_storage():
    rf = RequestFactory()
    request = rf.get("/")
    setattr(request, "session", {})
    setattr(request, "_messages", FallbackStorage(request))
    return request


def test_showcase_sidebar_translates_to_english() -> None:
    req = _request_with_message_storage()
    with translation.override("en"):
        resp = index(req)
    body = resp.content.decode()
    assert "Overview" in body
    assert "Panoramica" not in body
