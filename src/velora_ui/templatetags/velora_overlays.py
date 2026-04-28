"""Tooltip e helper per overlay (Fase 10 - v0.2).

Espone:
  - {% velora_tooltip "..." %}            -> attributi data-* da iniettare
                                              in un elemento esistente

Uso tipico:

    <button {% velora_tooltip "Modifica cliente" %}>...</button>

Il tag emette **solo** la stringa di attributi (senza tag esterno) cosi`
che possa essere inserita nel `<button>`/`<a>`/`<span>` desiderato senza
wrapper aggiuntivi. Il componente JS `tooltip` (vedi
`js/src/components/tooltip.js`) intercetta `mouseenter`/`focus` e mostra
un balloon flottante; `mouseleave`/`blur`/`Escape` lo chiudono.
"""

from __future__ import annotations

from django import template
from django.utils.html import escape
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


_VALID_PLACEMENTS = {"top", "bottom", "left", "right"}


@register.simple_tag
def velora_tooltip(
    text: str = "",
    placement: str = "top",
    delay: int = 200,
) -> SafeString:
    """Restituisce gli attributi HTML per fare di un elemento un trigger
    di tooltip.

    Args:
        text: contenuto del tooltip (testo, no HTML). Se vuoto la stringa
            ritorna vuota e nessun componente viene attaccato.
        placement: "top" (default), "bottom", "left", "right". Sconosciuto
            -> fallback "top".
        delay: ms prima di mostrare il tooltip al hover (default 200).
            Negativi -> 0.

    Esempio:
        <button {% velora_tooltip "Salva" placement="bottom" %}>OK</button>
    """

    if not text:
        return mark_safe("")
    if placement not in _VALID_PLACEMENTS:
        placement = "top"
    try:
        delay_int = max(0, int(delay))
    except (TypeError, ValueError):
        delay_int = 200
    parts = [
        ' data-velora-component="tooltip"',
        f' data-tooltip-text="{escape(text)}"',
        f' data-tooltip-placement="{placement}"',
        f' data-tooltip-delay="{delay_int}"',
    ]
    return mark_safe("".join(parts))
