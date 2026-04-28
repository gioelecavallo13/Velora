"""Template tag per dati tabellari e paginazione (M4 - Fase 6 del piano).

Espone:

  - {% velora_table headers=... rows=... %}
        Tabella statica `<table>` con `<thead>` e `<tbody>`. In v0.1 e`
        puramente di rendering: niente AJAX in cella, niente sort
        client-side, niente select_all_table_rows. Quelle funzioni sono
        rimandate a v0.3 (vedi piano "Cosa NON entra in v0.1").

  - {% velora_pagination page=... base_url=... param='page' %}
        Paginazione next/prev + numeri pagina. Accetta sia un oggetto Page
        del Paginator Django (interfaccia: number, paginator.num_pages,
        has_previous, has_next, previous_page_number, next_page_number)
        sia un dict equivalente con le stesse chiavi.

Schema dei dati per velora_table:

    headers = [
        "Nome",                                            # stringa = label
        {"key": "email", "label": "Email"},                # dict
        {"key": "actions", "label": "", "width": "120px"},
    ]

    rows = [
        ["Mario", "mario@x.it", "<a>...</a>"],             # list di celle
        {"name": "Luca", "email": "luca@y.it"},            # dict (richiede
                                                          #   `key` negli headers)
    ]
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode, urlsplit, urlunsplit

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


# ---------------------------------------------------------------------------
# velora_table
# ---------------------------------------------------------------------------


def _normalize_headers(raw: Any) -> list[dict[str, Any]]:
    """Converte gli header in lista di dict {label, key, width, extra_class}."""

    if not raw:
        return []
    normalized: list[dict[str, Any]] = []
    for entry in raw:
        if isinstance(entry, dict):
            normalized.append(
                {
                    "label": entry.get("label", entry.get("key", "")),
                    "key": entry.get("key"),
                    "width": entry.get("width", ""),
                    "extra_class": entry.get("extra_class", ""),
                    "align": entry.get("align", ""),
                }
            )
        else:
            normalized.append(
                {
                    "label": str(entry),
                    "key": None,
                    "width": "",
                    "extra_class": "",
                    "align": "",
                }
            )
    return normalized


def _normalize_rows(
    raw: Any, headers: list[dict[str, Any]]
) -> list[list[dict[str, Any]]]:
    """Converte le righe in liste di celle ``{value, align}`` allineate
    con gli header. Se una riga e` un dict, le celle si pescano per `key`;
    se e` una list/tuple, si prendono in ordine.
    """

    if not raw:
        return []

    table: list[list[dict[str, Any]]] = []
    for row in raw:
        cells: list[dict[str, Any]] = []
        if isinstance(row, dict):
            for header in headers:
                key = header.get("key")
                value = row.get(key, "") if key else ""
                cells.append(
                    {"value": value, "align": header.get("align", "")}
                )
        else:
            row_list = list(row)
            for index, header in enumerate(headers):
                value = row_list[index] if index < len(row_list) else ""
                cells.append(
                    {"value": value, "align": header.get("align", "")}
                )
        table.append(cells)
    return table


@register.simple_tag
def velora_table(
    headers: Any = None,
    rows: Any = None,
    empty_message: str = "Nessun risultato",
    extra_class: str = "",
    id: str = "",
) -> SafeString:
    """Render della tabella.

    Args:
        headers: vedi schema in modulo.
        rows: vedi schema in modulo.
        empty_message: testo mostrato se `rows` e` vuoto (cella unica
            colspan).
        extra_class: classi CSS extra sul `<table>`.
        id: id HTML opzionale.
    """

    norm_headers = _normalize_headers(headers)
    norm_rows = _normalize_rows(rows, norm_headers)
    ctx = {
        "headers": norm_headers,
        "rows": norm_rows,
        "empty_message": empty_message,
        "extra_class": extra_class,
        "id": id,
        "colspan": max(len(norm_headers), 1),
    }
    return mark_safe(
        render_to_string("velora_ui/components/table/_table.html", ctx)
    )


# ---------------------------------------------------------------------------
# velora_pagination
# ---------------------------------------------------------------------------


def _page_meta(page: Any) -> dict[str, Any]:
    """Estrae metadati di paginazione da un oggetto Page Django o da un dict.

    Ritorna un dict normalizzato:
      number, num_pages, has_previous, has_next,
      previous_page_number, next_page_number
    """

    if page is None:
        return {
            "number": 1,
            "num_pages": 1,
            "has_previous": False,
            "has_next": False,
            "previous_page_number": None,
            "next_page_number": None,
        }

    if isinstance(page, dict):
        number = int(page.get("number", 1))
        num_pages = int(page.get("num_pages", 1))
        has_previous = bool(page.get("has_previous", number > 1))
        has_next = bool(page.get("has_next", number < num_pages))
        return {
            "number": number,
            "num_pages": num_pages,
            "has_previous": has_previous,
            "has_next": has_next,
            "previous_page_number": number - 1 if has_previous else None,
            "next_page_number": number + 1 if has_next else None,
        }

    # Oggetto Page del Paginator Django (anatra-tipato)
    paginator = getattr(page, "paginator", None)
    num_pages = getattr(paginator, "num_pages", 1) if paginator else 1
    number = getattr(page, "number", 1)
    has_previous = bool(page.has_previous()) if hasattr(page, "has_previous") else False
    has_next = bool(page.has_next()) if hasattr(page, "has_next") else False
    return {
        "number": number,
        "num_pages": num_pages,
        "has_previous": has_previous,
        "has_next": has_next,
        "previous_page_number": (
            page.previous_page_number()
            if has_previous and hasattr(page, "previous_page_number")
            else None
        ),
        "next_page_number": (
            page.next_page_number()
            if has_next and hasattr(page, "next_page_number")
            else None
        ),
    }


def _build_page_window(number: int, num_pages: int, window: int = 5) -> list[int | None]:
    """Costruisce la finestra di pagine da mostrare.

    Mostra al massimo `window` pagine intorno alla corrente e usa `None`
    come marker per "..." dove c'e` un salto. Sempre incluse: pagina 1 e
    pagina `num_pages` (se entrambe esistono).
    """

    if num_pages <= 1:
        return [1]
    half = window // 2
    start = max(2, number - half)
    end = min(num_pages - 1, number + half)
    items: list[int | None] = [1]
    if start > 2:
        items.append(None)
    items.extend(range(start, end + 1))
    if end < num_pages - 1:
        items.append(None)
    if num_pages > 1:
        items.append(num_pages)
    return items


def _replace_query_param(url: str, param: str, value: Any) -> str:
    """Restituisce `url` con il parametro querystring `param` impostato a
    `value`. Conserva gli altri parametri e supporta URL relative."""

    if not url:
        return f"?{param}={value}"
    parts = urlsplit(url)
    pairs: list[tuple[str, str]] = []
    if parts.query:
        for chunk in parts.query.split("&"):
            if not chunk:
                continue
            if "=" in chunk:
                k, v = chunk.split("=", 1)
            else:
                k, v = chunk, ""
            if k != param:
                pairs.append((k, v))
    pairs.append((param, str(value)))
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(pairs), parts.fragment)
    )


@register.simple_tag
def velora_pagination(
    page: Any = None,
    base_url: str = "",
    param: str = "page",
    extra_class: str = "",
) -> SafeString:
    """Render della paginazione next/prev + finestra di numeri.

    Args:
        page: oggetto `Page` del `Paginator` Django oppure dict con
            `number`, `num_pages` (e opzionalmente `has_previous`,
            `has_next`).
        base_url: URL base su cui costruire i link. Se vuoto vengono
            generate URL del tipo `?page=N`.
        param: nome del parametro querystring (default "page").
        extra_class: classi CSS extra sul wrapper `<nav>`.
    """

    meta = _page_meta(page)

    pages: list[dict[str, Any]] = []
    if meta["num_pages"] > 0:
        for entry in _build_page_window(meta["number"], meta["num_pages"]):
            if entry is None:
                pages.append({"is_gap": True})
            else:
                pages.append(
                    {
                        "is_gap": False,
                        "number": entry,
                        "url": _replace_query_param(base_url, param, entry),
                        "is_current": entry == meta["number"],
                    }
                )

    ctx = {
        "meta": meta,
        "pages": pages,
        "previous_url": (
            _replace_query_param(base_url, param, meta["previous_page_number"])
            if meta["has_previous"]
            else ""
        ),
        "next_url": (
            _replace_query_param(base_url, param, meta["next_page_number"])
            if meta["has_next"]
            else ""
        ),
        "extra_class": extra_class,
    }
    return mark_safe(
        render_to_string("velora_ui/components/table/_pagination.html", ctx)
    )
