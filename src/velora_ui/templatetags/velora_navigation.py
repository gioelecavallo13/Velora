"""Template tag di navigazione e progress bar (Fase 10 - v0.2).

Espone:
  - {% velora_breadcrumb items=... %}
  - {% velora_submenu items=... title=... %}
  - {% velora_progress_bar value=... max=... %}                       (10.10)
  - {% velora_condensed_progress_breadcrumb steps=... current=... %}  (10.11)
  - {% velora_new_progress_bar current=... total=... %}               (10.12)

Convenzione: tutti i tag accettano dict malformati e li scartano
silenziosamente (non bloccano il render della pagina). Vedi AGENTS.md per
gli schemi formali.
"""

from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


_VALID_PROGRESS_VARIANTS = {"default", "success", "warning", "danger", "info"}


# -- velora_breadcrumb ----------------------------------------------------


def _normalize_breadcrumb_items(items: Any) -> list[dict[str, Any]]:
    """Filtra item senza label. L'ultimo item viene marcato `is_current`.

    Item validi accettano:
      - "label": str  required
      - "url":   str  default "" (l'ultimo item e` sempre senza link)
      - "icon":  str  default ""
    """

    if not items:
        return []
    out: list[dict[str, Any]] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        label = raw.get("label", "")
        if not label:
            continue
        out.append(
            {
                "label": label,
                "url": raw.get("url", ""),
                "icon": raw.get("icon", ""),
                "is_current": False,
            }
        )
    if out:
        out[-1]["is_current"] = True
    return out


@register.inclusion_tag("velora_ui/components/breadcrumb/_breadcrumb.html")
def velora_breadcrumb(
    items: Any = None,
    separator: str = "›",
    extra_class: str = "",
) -> dict[str, Any]:
    """Renderizza un breadcrumb come `<nav><ol>` con `aria-current="page"`
    sull'ultimo elemento. Se `items` e` vuoto/malformato il tag emette il
    nodo nav vuoto (con aria-label) ma niente lista.
    """

    return {
        "items": _normalize_breadcrumb_items(items),
        "separator": separator,
        "extra_class": extra_class,
    }


# -- velora_submenu -------------------------------------------------------


def _normalize_submenu_items(items: Any) -> list[dict[str, Any]]:
    if not items:
        return []
    out: list[dict[str, Any]] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        label = raw.get("label", "")
        url = raw.get("url", "")
        if not label or not url:
            continue
        out.append(
            {
                "label": label,
                "url": url,
                "icon": raw.get("icon", ""),
                "active": bool(raw.get("active", False)),
                "extra_class": raw.get("extra_class", ""),
            }
        )
    return out


@register.inclusion_tag("velora_ui/components/submenu/_submenu.html")
def velora_submenu(
    items: Any = None,
    title: str = "",
    extra_class: str = "",
) -> dict[str, Any]:
    """Renderizza un sotto-menu verticale con titolo opzionale.

    Pattern d'uso: pannello laterale di una pagina detail, gruppo di link
    in un card, sezione "azioni rapide". Per il menu globale dell'app si
    usa la sidebar (`velora_ui/base.html`).
    """

    return {
        "items": _normalize_submenu_items(items),
        "title": title,
        "extra_class": extra_class,
    }


# -- velora_progress_bar (10.10 - classico) -------------------------------


def _coerce_number(raw: Any, default: float) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def _percent_from_value(value: float, max_value: float) -> float:
    """Mappa value/max in [0..100] con safety. value<=0 -> 0, value>=max -> 100."""

    if max_value <= 0:
        return 0.0
    pct = (value / max_value) * 100.0
    if pct < 0:
        return 0.0
    if pct > 100:
        return 100.0
    return pct


@register.inclusion_tag("velora_ui/components/progress/_progress_bar.html")
def velora_progress_bar(
    value: Any = 0,
    max: Any = 100,  # noqa: A002 (`max` shadow del builtin: scelta API voluta)
    label: str = "",
    variant: str = "default",
    show_percent: bool = True,
    extra_class: str = "",
) -> dict[str, Any]:
    """Progress bar classica.

    - `value` e `max` accettano int/float/string castable.
    - `variant` valide: default, success, warning, danger, info. Variant
      sconosciuta -> fallback "default".
    - Render: `<div role="progressbar" aria-valuenow=... aria-valuemax=...>`
      con barra interna larga `width: <pct>%`.
    """

    v = _coerce_number(value, 0.0)
    m = _coerce_number(max, 100.0)
    pct = _percent_from_value(v, m)
    if variant not in _VALID_PROGRESS_VARIANTS:
        variant = "default"
    return {
        "label": label,
        "variant": variant,
        "show_percent": bool(show_percent),
        "extra_class": extra_class,
        "value": v,
        "max": m,
        # Stringa con 2 decimali stabili; il template fa `style="width: {{ pct }}%"`.
        "pct": f"{pct:.2f}",
        "pct_int": int(round(pct)),
    }


# -- velora_condensed_progress_breadcrumb (10.11) -------------------------


def _normalize_steps(steps: Any) -> list[dict[str, Any]]:
    """Accetta una lista di stringhe (label) oppure di dict
    `{"label": "...", "url"?: "..."}`.
    """

    if not steps:
        return []
    out: list[dict[str, Any]] = []
    for raw in steps:
        if isinstance(raw, str):
            label = raw
            url = ""
        elif isinstance(raw, dict):
            label = raw.get("label", "")
            url = raw.get("url", "")
        else:
            continue
        if not label:
            continue
        out.append({"label": label, "url": url})
    return out


@register.inclusion_tag(
    "velora_ui/components/progress/_condensed_breadcrumb.html"
)
def velora_condensed_progress_breadcrumb(
    steps: Any = None,
    current: Any = 1,
    extra_class: str = "",
) -> dict[str, Any]:
    """Breadcrumb di progresso a fasi numerate (es. wizard 1->2->3).

    `current` e` 1-based: il primo step e` `current=1`. Valori fuori range
    vengono clampati. Ogni step viene reso con stato `done` / `current` /
    `upcoming` per consentire styling differenziato. Numerazione
    automatica `1, 2, 3, ...` mostrata nel pallino.
    """

    items = _normalize_steps(steps)
    total = len(items)
    if total == 0:
        return {"steps": [], "extra_class": extra_class, "current": 0, "total": 0}

    cur_raw = _coerce_number(current, 1.0)
    cur = int(cur_raw)
    if cur < 1:
        cur = 1
    if cur > total:
        cur = total

    enriched: list[dict[str, Any]] = []
    for idx, item in enumerate(items, start=1):
        if idx < cur:
            status = "done"
        elif idx == cur:
            status = "current"
        else:
            status = "upcoming"
        enriched.append(
            {
                "index": idx,
                "label": item["label"],
                "url": item["url"],
                "status": status,
                "is_done": status == "done",
                "is_current": status == "current",
            }
        )
    return {
        "steps": enriched,
        "current": cur,
        "total": total,
        "extra_class": extra_class,
    }


# -- velora_new_progress_bar (10.12 - "X di Y") ---------------------------


@register.inclusion_tag("velora_ui/components/progress/_new_progress_bar.html")
def velora_new_progress_bar(
    current: Any = 0,
    total: Any = 0,
    label: str = "",
    variant: str = "default",
    extra_class: str = "",
) -> dict[str, Any]:
    """Progress bar "X di Y": utile per upload, batch, sondaggi.

    Mostra contatore `current di total` + barra. Se `total <= 0` il
    componente mostra label e contatore ma nessuna barra (graceful).
    """

    c = int(_coerce_number(current, 0.0))
    t = int(_coerce_number(total, 0.0))
    if c < 0:
        c = 0
    if t < 0:
        t = 0
    if t > 0 and c > t:
        c = t
    pct = (c / t * 100.0) if t > 0 else 0.0
    if variant not in _VALID_PROGRESS_VARIANTS:
        variant = "default"
    return {
        "current": c,
        "total": t,
        "label": label,
        "variant": variant,
        "has_bar": t > 0,
        "pct": f"{pct:.2f}",
        "pct_int": int(round(pct)),
        "extra_class": extra_class,
    }
