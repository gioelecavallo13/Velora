"""Template tag per grafici Chart.js da tabella HTML (Fase 12.1 — `velora_chart`).

Carica con ``{% load velora_chart %}``. Richiede che la pagina includa il
bundle ``velora.js`` (gia` contiene Chart.js a partire da v0.4.0).

Il tag emette un wrapper con ``<canvas>`` e attributi ``data-*`` che il
componente ``chart-from-table`` legge al boot: trova la tabella via selettore
CSS, estrae labels e serie numeriche, istanzia ``Chart``.

Convenzioni tabella
-------------------

**line** e **bar** (serie multiple):

- ``<thead><tr>``: primo ``<th>`` puo` essere vuoto o etichetta asse; gli altri
  ``<th>`` sono le etichette dell'asse X (categorie).
- ``<tbody>``: ogni ``<tr>`` ha primo ``<td>`` = nome serie, i successivi = valori
  numerici allineati alle colonne dell'header (esclusa la prima).

**pie** (torta):

- ``<tbody>``: ogni riga ha esattamente due celle: etichetta fetta e valore
  numerico. ``<thead>`` opzionale a due colonne.

Esempio::

    <table id="sales-q">
      <thead><tr><th></th><th>Q1</th><th>Q2</th><th>Q3</th></tr></thead>
      <tbody>
        <tr><td>Italia</td><td>10</td><td>20</td><td>15</td></tr>
        <tr><td>Germania</td><td>5</td><td>8</td><td>12</td></tr>
      </tbody>
    </table>
    {% velora_chart_from_table table_selector="#sales-q" chart_type="bar" canvas_id="ch-sales" %}
"""

from __future__ import annotations

from typing import Any

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe

from velora_ui.chartutils import normalize_chart_type

register = template.Library()


@register.simple_tag
def velora_chart_from_table(
    table_selector: str = "",
    chart_type: str = "line",
    canvas_id: str = "",
    height: int | str = 280,
    extra_class: str = "",
) -> SafeString:
    """Renderizza wrapper + canvas per un grafico costruito da una tabella.

    Args:
        table_selector: selettore CSS della tabella sorgente (es. ``#my-table``).
            Se vuoto il tag non emette markup.
        chart_type: ``line`` | ``bar`` | ``pie`` (case-insensitive;
            sconosciuto -> ``line``).
        canvas_id: id HTML del ``<canvas>``. Se vuoto viene generato
            ``velora-chart-canvas`` (attenzione a id duplicati se piu` grafici).
        height: altezza CSS del box in pixel (numero o stringa numerica).
        extra_class: classi aggiuntive sul wrapper.

    Returns:
        HTML safe del wrapper.
    """

    if not (table_selector or "").strip():
        return mark_safe("")

    ct = normalize_chart_type(chart_type)
    cid = (canvas_id or "").strip() or "velora-chart-canvas"
    try:
        h = int(height)
    except (TypeError, ValueError):
        h = 280
    if h < 80:
        h = 80

    ctx: dict[str, Any] = {
        "table_selector": table_selector.strip(),
        "chart_type": ct,
        "canvas_id": cid,
        "height_px": h,
        "extra_class": extra_class or "",
    }
    return mark_safe(
        render_to_string("velora_ui/components/chart/_from_table.html", ctx)
    )
