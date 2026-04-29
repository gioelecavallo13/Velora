"""Visual regression del living styleguide (M6 - Fase 8 del piano).

Per ogni sezione dello showcase scattiamo uno screenshot full-page con
Chromium, lo confrontiamo bytewise contro la baseline in
``tests/visual/__snapshots__/`` e:

  - ``--update-snapshots`` -> sovrascrive la baseline col nuovo screenshot
  - assenza di baseline   -> il test fallisce con un messaggio chiaro
  - byte mismatch         -> il test fallisce salvando l'attuale come
                              ``<name>.actual.png`` accanto alla baseline
                              per ispezione manuale (diff a occhio)

Il confronto e` puramente bytewise: non usiamo Pillow/pixelmatch per
restare a zero-dipendenze extra. La viewport fissa + il container
deterministico (immagine Microsoft Playwright) riducono il rumore al
livello accettabile per un v0.1; per v0.2 valuteremo un compare con
tolleranza.
"""

from __future__ import annotations

from pathlib import Path

import pytest


SNAPSHOT_DIR = Path(__file__).parent / "__snapshots__"

# (nome_baseline, anchor, descrizione_human)
SECTIONS = [
    ("overview", "#overview", "Hero / overview"),
    ("layout", "#layout", "Layout core"),
    ("form", "#form", "Form core"),
    ("tables", "#tables", "Tabelle e paginazione"),
    ("links", "#links", "Link essenziali"),
    ("feedback", "#feedback", "Feedback"),
    # v0.2 — Fase 10
    ("navigation", "#navigation", "Navigation v0.2"),
    ("overlays", "#overlays", "Overlays v0.2"),
    ("progress", "#progress", "Progress v0.2"),
    # v0.3 — Fase 11
    ("form-advanced", "#form-advanced", "Form avanzati v0.3"),
    ("tables-advanced", "#tables-advanced", "Tabelle interattive v0.3"),
    ("checkbox", "#checkbox", "Checkbox tag v0.3"),
]


def _baseline_path(name: str) -> Path:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    return SNAPSHOT_DIR / f"{name}.png"


def _actual_path(name: str) -> Path:
    return SNAPSHOT_DIR / f"{name}.actual.png"


def _compare_or_update(
    name: str, png_bytes: bytes, update: bool
) -> None:
    baseline = _baseline_path(name)
    if update or not baseline.exists():
        baseline.write_bytes(png_bytes)
        if not update:
            pytest.fail(
                f"baseline mancante per '{name}', creata ora in {baseline}. "
                "Rilancia i test per validarla."
            )
        return

    if baseline.read_bytes() == png_bytes:
        # match esatto, eventuale .actual stantio rimosso
        actual = _actual_path(name)
        if actual.exists():
            actual.unlink()
        return

    actual = _actual_path(name)
    actual.write_bytes(png_bytes)
    pytest.fail(
        f"snapshot '{name}' diverso dalla baseline. "
        f"Confronta {actual} con {baseline}; se il cambio e` voluto, "
        f"rilancia con --update-snapshots."
    )


@pytest.mark.parametrize("name,anchor,_label", SECTIONS, ids=[s[0] for s in SECTIONS])
def test_showcase_section_snapshot(
    name: str,
    anchor: str,
    _label: str,
    page,
    velora_url: str,
    update_snapshots: bool,
) -> None:
    """Snapshot della sezione `anchor` dello showcase."""

    page.goto(f"{velora_url}/{anchor}")
    page.wait_for_load_state("networkidle")
    # Rimuoviamo eventuali toast residui (potrebbero apparire se la URL
    # contiene ?toast=...) per non rendere lo snapshot non-deterministico.
    page.evaluate(
        "document.querySelectorAll('.velora-toast-container').forEach(n => n.remove())"
    )
    locator = page.locator(f"section{anchor}")
    locator.scroll_into_view_if_needed()
    png = locator.screenshot()
    _compare_or_update(name, png, update_snapshots)


def test_showcase_full_page_snapshot(page, velora_url, update_snapshots) -> None:
    """Snapshot full-page dello showcase intero (regressioni di layout)."""

    page.goto(velora_url)
    page.wait_for_load_state("networkidle")
    page.evaluate(
        "document.querySelectorAll('.velora-toast-container').forEach(n => n.remove())"
    )
    png = page.screenshot(full_page=True)
    _compare_or_update("full_page", png, update_snapshots)
