"""Test endpoint AJAX catalogo Ionicons (showcase)."""

from __future__ import annotations

import pytest
from django.test import Client


@pytest.mark.django_db
def test_ionicons_search_ajax_filter(client: Client) -> None:
    r = client.get("/api/ionicons/", {"q": "home"})
    assert r.status_code == 200
    data = r.json()
    assert "icons" in data
    assert data["total_icons"] > 50
    assert data["is_initial"] is False
    assert any("home" in slug for slug in data["icons"])


@pytest.mark.django_db
def test_ionicons_search_initial_window(client: Client) -> None:
    r = client.get("/api/ionicons/")
    assert r.status_code == 200
    data = r.json()
    assert data["is_initial"] is True
    assert len(data["icons"]) <= 96
    assert data["total_icons"] >= len(data["icons"])


@pytest.mark.django_db
def test_ionicons_search_tutte_respects_limit(client: Client) -> None:
    r = client.get("/api/ionicons/", {"q": "tutte", "limit": 99999})
    assert r.status_code == 200
    data = r.json()
    assert len(data["icons"]) <= 2000
    assert data["matched"] == data["total_icons"]


@pytest.mark.django_db
def test_ionicons_search_method_not_allowed(client: Client) -> None:
    r = client.post("/api/ionicons/")
    assert r.status_code == 405
