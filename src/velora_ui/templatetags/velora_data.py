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


@register.filter
def index_or_empty(seq: Any, idx: int) -> str:
    """Filtro template: ritorna seq[idx] o "" se fuori range."""
    try:
        return str(seq[int(idx)])
    except (IndexError, TypeError, ValueError):
        return ""


# ---------------------------------------------------------------------------
# v0.3 — form-in-cell schema
# ---------------------------------------------------------------------------
#
# Una cella di `velora_table` puo` essere:
#
#   1. Stringa o numero        -> render testo plain (v0.1)
#   2. Markup pre-renderizzato -> mark_safe lato view (v0.1)
#   3. Dict {form_in_cell: {...}} -> input editabile inline (v0.3)
#
# Schema `form_in_cell`:
#
#     {
#         "type": "text" | "select" | "checkbox" | "onoff",   # required
#         "name": str,           # required (chiave per il backend)
#         "value": Any,          # default ""
#         "url": str,            # required: endpoint PATCH/POST
#         "method": "patch"|"post"|"put",  # default "patch"
#         "csrf": bool,          # default True (legge __velora_csrf__ globale)
#         "auto_submit": bool,   # default True (debounce 400ms; False = submit
#                                #  manuale via tasto Enter o blur)
#         "choices": [...],      # solo per type=select
#         "row_id": str|int,     # opzionale; il client lo passa nel body
#                                #  come campo "id"
#     }
#
# Lato client: componente `table-cell` ascolta change/blur, costruisce
# FormData o JSON body, fa fetch() con CSRF token Django.
# ---------------------------------------------------------------------------


_VALID_FIC_TYPES = {"text", "number", "select", "checkbox", "onoff"}
_VALID_FIC_METHODS = {"patch", "post", "put"}


def _normalize_fic_choices(raw: Any) -> list[dict[str, Any]]:
    """Stesso shape di velora_forms._normalize_choices ma duplicato qui per
    non creare dipendenza cross-tag."""
    if not raw:
        return []
    out: list[dict[str, Any]] = []
    for entry in raw:
        if isinstance(entry, dict):
            out.append(
                {
                    "value": entry.get("value", ""),
                    "label": entry.get("label", entry.get("value", "")),
                }
            )
        elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
            out.append({"value": entry[0], "label": entry[1]})
        else:
            out.append({"value": entry, "label": entry})
    return out


def _normalize_form_in_cell(raw: Any) -> dict[str, Any] | None:
    """Valida e normalizza un form_in_cell; ritorna None se invalido."""
    if not isinstance(raw, dict):
        return None
    fic_type = raw.get("type", "")
    if fic_type not in _VALID_FIC_TYPES:
        return None
    name = raw.get("name", "")
    url = raw.get("url", "")
    if not name or not url:
        return None
    method = str(raw.get("method", "patch")).lower()
    if method not in _VALID_FIC_METHODS:
        method = "patch"
    normalized: dict[str, Any] = {
        "type": fic_type,
        "name": name,
        "value": raw.get("value", ""),
        "url": url,
        "method": method,
        "csrf": bool(raw.get("csrf", True)),
        "auto_submit": bool(raw.get("auto_submit", True)),
        "row_id": raw.get("row_id", ""),
    }
    if fic_type == "select":
        normalized["choices"] = _normalize_fic_choices(raw.get("choices"))
    return normalized


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


def _build_cell(value: Any, align: str) -> dict[str, Any]:
    """Costruisce una cella normalizzata, riconoscendo lo schema form-in-cell.

    Una cella e` un dict con campi:
      value        : testo/HTML da mostrare quando NON c'e` form-in-cell
      align        : '' | 'right' | 'center'
      form_in_cell : dict normalizzato (None se cella semplice)

    Se `value` e` un dict con chiave `form_in_cell`, il relativo schema
    viene validato; valori sotto la chiave `value` (label visualizzata
    quando il campo non e` editabile) sono passati come fallback.
    """
    if isinstance(value, dict) and "form_in_cell" in value:
        fic = _normalize_form_in_cell(value["form_in_cell"])
        return {
            "value": value.get("value", ""),
            "align": align,
            "form_in_cell": fic,
        }
    return {"value": value, "align": align, "form_in_cell": None}


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
                cells.append(_build_cell(value, header.get("align", "")))
        else:
            row_list = list(row)
            for index, header in enumerate(headers):
                value = row_list[index] if index < len(row_list) else ""
                cells.append(_build_cell(value, header.get("align", "")))
        table.append(cells)
    return table


@register.simple_tag
def velora_table(
    headers: Any = None,
    rows: Any = None,
    empty_message: str = "Nessun risultato",
    extra_class: str = "",
    id: str = "",
    selectable: bool = False,
    row_id_key: str = "id",
) -> SafeString:
    """Render della tabella.

    Args:
        headers: vedi schema in modulo.
        rows: vedi schema in modulo.
        empty_message: testo mostrato se `rows` e` vuoto (cella unica
            colspan).
        extra_class: classi CSS extra sul `<table>`.
        id: id HTML opzionale.
        selectable: (v0.3) se True aggiunge una colonna iniziale con
            checkbox per riga (compatibili con `velora_select_all_table_rows`).
            Le righe devono essere dict per esporre `row_id_key` come id.
        row_id_key: (v0.3) chiave usata per leggere l'id della riga
            (default "id"). Ignorato se `selectable=False` o se la riga
            e` lista posizionale.
    """

    norm_headers = _normalize_headers(headers)
    norm_rows = _normalize_rows(rows, norm_headers)
    row_ids: list[str] = []
    if selectable:
        for row in raw_iter(rows):
            if isinstance(row, dict):
                row_ids.append(str(row.get(row_id_key, "")))
            else:
                row_ids.append("")
    ctx = {
        "headers": norm_headers,
        "rows": norm_rows,
        "empty_message": empty_message,
        "extra_class": extra_class,
        "id": id,
        "selectable": bool(selectable),
        "row_ids": row_ids,
        "colspan": max(len(norm_headers), 1) + (1 if selectable else 0),
    }
    return mark_safe(
        render_to_string("velora_ui/components/table/_table.html", ctx)
    )


def raw_iter(raw: Any) -> list[Any]:
    """Helper interno: ritorna sempre una lista (anche da iterabili)."""
    if not raw:
        return []
    return list(raw)


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


# ---------------------------------------------------------------------------
# velora_select_all_table_rows (v0.3 — Fase 11.11)
# ---------------------------------------------------------------------------


def _normalize_bulk_actions(raw: Any) -> list[dict[str, Any]]:
    """Normalizza la lista di bulk actions in
    [{label, value, url?, method?, variant?}].

    `value`: identificativo passato come `action` nella request.
    `url`: opzionale (default = la URL del tag, gestita lato JS).
    `method`: post|patch|delete (default post).
    `variant`: primary|secondary|danger (default secondary; danger evidenziato).
    Item senza `label` o `value` scartato.
    """
    if not raw:
        return []
    out: list[dict[str, Any]] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        label = entry.get("label", "")
        value = entry.get("value", "")
        if not label or not value:
            continue
        method = str(entry.get("method", "post")).lower()
        if method not in {"post", "patch", "delete"}:
            method = "post"
        variant = entry.get("variant", "secondary")
        if variant not in {"primary", "secondary", "danger"}:
            variant = "secondary"
        out.append(
            {
                "label": label,
                "value": value,
                "url": entry.get("url", ""),
                "method": method,
                "variant": variant,
                "confirm": entry.get("confirm", ""),
            }
        )
    return out


@register.simple_tag
def velora_select_all_table_rows(
    target: str = "",
    actions: Any = None,
    url: str = "",
    name: str = "ids",
    label: str = "",
    extra_class: str = "",
) -> SafeString:
    """Toolbar bulk-actions agganciata a una tabella `selectable=True`.

    Args:
        target: selettore CSS della tabella (es. "#tabella-clienti").
            Se vuoto il tag non emette nulla.
        actions: lista di azioni; vedi `_normalize_bulk_actions`.
        url: URL endpoint che riceve la POST/PATCH dei bulk; il body
            include `action=<value>` e `<name>=id1,id2,...`.
        name: nome del campo che contiene gli id selezionati (default "ids").
        label: testo a sinistra (es. "Selezionati:" — il contatore vivo
            e` aggiunto dal JS).
        extra_class: classi extra sul wrapper.

    Render: `<div data-velora-component="select-all-table">`. Il JS
    `select_all.js` aggancia la checkbox master del target, sincronizza
    con le checkbox di riga, mostra il contatore "(N)" e gestisce il
    submit AJAX delle azioni.
    """
    if not target:
        return mark_safe("")
    ctx = {
        "target": target,
        "actions": _normalize_bulk_actions(actions),
        "url": url,
        "name": name,
        "label": label or "Selezionati",
        "extra_class": extra_class,
    }
    return mark_safe(
        render_to_string("velora_ui/components/table/_select_all.html", ctx)
    )
