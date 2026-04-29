"""Utilita` per l'integrazione Chart.js da tabella HTML (Fase 12.1).

Il parsing dei numeri e la creazione del grafico avvengono lato client nel
componente JS ``chart-from-table``. Questo modulo espone solo costanti e
normalizzazione usate dai template tag ``velora_chart``.
"""

from __future__ import annotations

VALID_CHART_TYPES = frozenset({"line", "bar", "pie"})


def normalize_chart_type(raw: str | None) -> str:
    """Ritorna uno fra line|bar|pie; valori sconosciuti -> ``line``."""

    s = (raw or "line").strip().lower()
    return s if s in VALID_CHART_TYPES else "line"
