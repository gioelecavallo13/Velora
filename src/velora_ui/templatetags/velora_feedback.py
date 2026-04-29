"""Template tag di feedback per Velora UI (M5 - Fase 7 del piano).

Espone:

  - {% velora_alert variant='success' message='...' dismissible=True %}
        Alert inline (banner) con 4 varianti: success, error, warning, info.

  - {% velora_label variant='success' text='Attivo' %}
        Badge inline (pillola) per evidenziare stati: 5 varianti
        (success, error, warning, info, neutral).

  - {% velora_toast_messages %}
        Riemette i messaggi del framework `django.contrib.messages` come
        toast Velora: per ogni messaggio rende un blocco
        `<script data-velora-toast type="application/json">` letto al
        DOMContentLoaded dal componente JS `toast.js` (vedi 7.2).
        Cosi` la view non deve sapere nulla di JS: basta fare
        ``messages.success(request, "...")``.

  - {% velora_satisfaction_bar value=3 max_value=5 label="..." variant="default" %}
        Barra a segmenti orizzontali per KPI o soddisfazione (varianti
        default / success / danger).
"""

from __future__ import annotations

import json
from typing import Any

from django import template
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


def _coerce_nonneg_int(val: Any, default: int) -> int:
    try:
        i = int(val)
    except (TypeError, ValueError):
        return default
    return max(0, i)


_ALERT_VARIANTS = {"success", "error", "warning", "info"}
_LABEL_VARIANTS = {"success", "error", "warning", "info", "neutral"}
_SATISFACTION_VARIANTS = frozenset({"default", "success", "danger"})


# Mappatura dei livelli `messages` Django alle varianti Velora.
# `messages.WARNING` corrisponde a "warning", `ERROR`/`CRITICAL` a "error",
# `SUCCESS` a "success", `INFO`/`DEBUG` a "info".
_MESSAGES_LEVEL_MAP: dict[int, str] = {
    messages.DEBUG: "info",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "error",
}


@register.simple_tag
def velora_alert(
    variant: str = "info",
    message: str = "",
    title: str = "",
    dismissible: bool = False,
    extra_class: str = "",
) -> SafeString:
    """Renderizza un alert inline.

    Args:
        variant: una fra success, error, warning, info. Variante invalida =
            fallback a "info".
        message: testo principale dell'alert.
        title: titolo opzionale (mostrato in grassetto sopra il messaggio).
        dismissible: se True aggiunge un bottone X che rimuove il nodo dal
            DOM. La logica e` puro JS inline minimale (no componente
            registrato perche` non serve auto-init).
        extra_class: classi CSS extra sul wrapper.
    """

    if variant not in _ALERT_VARIANTS:
        variant = "info"
    return mark_safe(
        render_to_string(
            "velora_ui/components/feedback/_alert.html",
            {
                "variant": variant,
                "message": message,
                "title": title,
                "dismissible": dismissible,
                "extra_class": extra_class,
            },
        )
    )


@register.simple_tag
def velora_label(
    variant: str = "neutral",
    text: str = "",
    extra_class: str = "",
) -> SafeString:
    """Renderizza un badge inline.

    Variants v0.1: success, error, warning, info, neutral. Invalido =
    fallback a "neutral".
    """

    if variant not in _LABEL_VARIANTS:
        variant = "neutral"
    return mark_safe(
        render_to_string(
            "velora_ui/components/feedback/_label.html",
            {
                "variant": variant,
                "text": text,
                "extra_class": extra_class,
            },
        )
    )


@register.simple_tag(takes_context=True)
def velora_toast_messages(context: template.Context) -> SafeString:
    """Riemette i messaggi del framework `django.contrib.messages` come
    payload JSON che il componente JS `toast.js` consuma a DOMContentLoaded.

    Pattern d'uso: nel `base.html` o nella pagina aggiungere

        {% velora_toast_messages %}

    in coda al body. Le view popolano i messaggi con

        messages.success(request, "Salvato")
        messages.error(request, "Operazione fallita")

    e Velora li mostra come toast senza bisogno di JS custom.

    Implementazione:
      1. legge ``request._messages`` o usa ``messages.get_messages(request)``
      2. mappa il level Django sulla variante Velora
      3. emette uno `<script type="application/json" data-velora-toast>`
         per messaggio (no `<script>` eseguibili: il componente toast
         legge gli script di tipo application/json al boot)
    """

    request = context.get("request")
    if request is None:
        return mark_safe("")

    storage = messages.get_messages(request)
    items: list[dict[str, Any]] = []
    for msg in storage:
        variant = _MESSAGES_LEVEL_MAP.get(msg.level, "info")
        items.append(
            {
                "variant": variant,
                "message": str(msg.message),
                # `extra_tags` di Django diventa data-velora-toast-tags,
                # cosi` la view puo` aggiungere ad es. "persistent" per
                # disattivare l'auto-dismiss
                "tags": msg.extra_tags or "",
            }
        )
    storage.used = True

    if not items:
        return mark_safe("")

    chunks: list[str] = []
    for item in items:
        # `application/json` non e` eseguibile: lo decodifichiamo lato JS.
        # `json.dumps` con ensure_ascii=False produce stringhe leggibili.
        # Escape di "</" per evitare break-out dello script tag (paranoia).
        payload = json.dumps(item, ensure_ascii=False).replace("</", "<\\/")
        chunks.append(
            f'<script type="application/json" data-velora-toast>{payload}</script>'
        )
    return mark_safe("\n".join(chunks))


@register.inclusion_tag("velora_ui/components/feedback/_satisfaction_bar.html")
def velora_satisfaction_bar(
    value: Any = 0,
    max_value: Any = 5,
    label: str = "",
    variant: str = "default",
    aria_label: str = "",
    extra_class: str = "",
) -> dict[str, Any]:
    """Segmenti orizzontali: i primi `value` su `max_value` sono \"riempiti\"."""

    mx = _coerce_nonneg_int(max_value, 5)
    if mx <= 0:
        mx = 5
    v = _coerce_nonneg_int(value, 0)
    filled = min(v, mx)
    var = variant if variant in _SATISFACTION_VARIANTS else "default"
    segments = list(range(mx))
    aria = (aria_label or "").strip()
    if not aria and label:
        aria = str(label)
    return {
        "show": True,
        "filled": filled,
        "segments": segments,
        "label": label,
        "variant": var,
        "extra_class": extra_class or "",
        "aria_label": aria,
    }
