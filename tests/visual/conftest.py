"""conftest dei test visual con Playwright (M6 - Fase 8 del piano).

I test in `tests/visual/` girano in un container dedicato basato su
``mcr.microsoft.com/playwright/python`` (vedi servizio `playwright-tests`
in docker-compose.dev.yml), perche` il container `web` di sviluppo non ha
le librerie di sistema necessarie per Chromium / Firefox / WebKit.

Esecuzione:

    docker compose -f docker-compose.dev.yml run --rm playwright-tests

Aggiornare le baseline:

    docker compose -f docker-compose.dev.yml run --rm \\
        playwright-tests pytest tests/visual --update-snapshots
"""

from __future__ import annotations

import os

import pytest


def pytest_addoption(parser):
    """Aggiunge l'opzione `--update-snapshots` per rigenerare le baseline."""

    parser.addoption(
        "--update-snapshots",
        action="store_true",
        default=False,
        help="Salva i nuovi screenshot come baseline invece di confrontare.",
    )


@pytest.fixture(scope="session")
def update_snapshots(request) -> bool:
    return request.config.getoption("--update-snapshots")


@pytest.fixture(scope="session")
def velora_url() -> str:
    """URL della showcase a cui puntare.

    Default: ``http://web:8000`` (il servizio `web` raggiungibile via
    network di compose). Override con env ``VELORA_VISUAL_URL`` per
    eseguire i test contro un'altra istanza (es. velora.local dall'host).
    """

    return os.environ.get("VELORA_VISUAL_URL", "http://web:8000")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Forza una viewport deterministica per ridurre il rumore degli
    screenshot fra macchine diverse."""

    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 800},
        "device_scale_factor": 1,
        "locale": "it-IT",
        "timezone_id": "Europe/Rome",
    }
