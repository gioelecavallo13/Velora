"""Link template tag (M4 v0.1 + estensioni v0.2 - Fase 10 del piano).

V0.1 (M4):
  - {% velora_action_link  url=... label=... %}  -> azione "principale" arancio
  - {% velora_nav_link     url=... label=... %}  -> link di navigazione blu
  - {% velora_delete_link  url=... %}            -> azione distruttiva rossa
  - {% velora_btn_link     url=... label=... %}  -> bottone-link generico

V0.2 (Fase 10):
  - {% velora_settings_link url=... %}            -> verde, configurazioni
  - {% velora_toggle_link target="#x" %}          -> mostra/nasconde + alterna label
  - {% velora_copy_link    value="..." %}         -> clipboard + toast feedback
  - {% velora_drop_down_link   label=... items=... %}   -> link con dropdown
  - {% velora_drop_down_button label=... items=... %}   -> bottone con dropdown
  - {% velora_open_dialog_action_link target="#m" %}    -> apre dialog modale

Convenzioni comuni:
  - Tutti i tag accettano `extra_class`, e quando applicabile `target`,
    `rel`, `title`, `disabled`.
  - L'output e` SafeString.
  - Per evitare XSS i parametri stringa passano comunque attraverso
    `escape()` / `format_html()` -- non costruiamo HTML grezzo da input
    utente.
"""

from __future__ import annotations

from typing import Any

from django import template
from django.utils.html import conditional_escape, escape, format_html
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


def _attr(name: str, value: Any) -> str:
    """Helper: rende `name="escaped_value"` o "" se value falsy."""

    if value is None or value == "" or value is False:
        return ""
    if value is True:
        return f" {name}"
    return f' {name}="{escape(value)}"'


def _build_link(
    url: str,
    label: str,
    *,
    base_class: str,
    extra_class: str = "",
    title: str = "",
    target: str = "",
    rel: str = "",
    disabled: bool = False,
    extra_attrs: dict[str, Any] | None = None,
) -> SafeString:
    """Costruisce un `<a>` Velora con escape su tutti gli attributi."""

    classes = base_class
    if extra_class:
        classes = f"{classes} {extra_class}"
    if disabled:
        classes = f"{classes} is-disabled"

    attrs: list[str] = []
    attrs.append(_attr("title", title))
    attrs.append(_attr("target", target))
    if rel:
        attrs.append(_attr("rel", rel))
    elif target == "_blank":
        # default sicuro per link esterni in tab nuova
        attrs.append(_attr("rel", "noopener noreferrer"))
    if disabled:
        attrs.append(_attr("aria-disabled", "true"))
        attrs.append(_attr("tabindex", "-1"))
    if extra_attrs:
        for k, v in extra_attrs.items():
            attrs.append(_attr(k, v))

    href = "#" if disabled else (url or "#")
    return mark_safe(
        format_html(
            '<a href="{}" class="{}"{}>{}</a>',
            href,
            classes,
            mark_safe("".join(attrs)),
            label,
        )
    )


@register.simple_tag
def velora_action_link(
    url: str = "",
    label: str = "",
    title: str = "",
    target: str = "",
    rel: str = "",
    disabled: bool = False,
    extra_class: str = "",
) -> SafeString:
    """Link "azione principale" (arancio) usato per primary action delle
    tabelle (es. "Modifica") e per le call-to-action della title bar."""

    return _build_link(
        url,
        label,
        base_class="velora-link velora-link-action",
        extra_class=extra_class,
        title=title,
        target=target,
        rel=rel,
        disabled=disabled,
    )


@register.simple_tag
def velora_nav_link(
    url: str = "",
    label: str = "",
    title: str = "",
    target: str = "",
    rel: str = "",
    disabled: bool = False,
    extra_class: str = "",
) -> SafeString:
    """Link di navigazione (blu, sobrio) per spostarsi fra viste e detail."""

    return _build_link(
        url,
        label,
        base_class="velora-link velora-link-nav",
        extra_class=extra_class,
        title=title,
        target=target,
        rel=rel,
        disabled=disabled,
    )


@register.simple_tag
def velora_delete_link(
    url: str = "",
    label: str = "Elimina",
    confirm_message: str = "Confermi l'eliminazione?",
    method: str = "post",
    title: str = "",
    extra_class: str = "",
    disabled: bool = False,
) -> SafeString:
    """Link "distruttivo" (rosso) per eliminazioni.

    Aggiunge `data-velora-component="confirm"` cosi` il componente JS
    omonimo intercetta il click, mostra una `confirm()` e -- se l'utente
    conferma -- crea al volo un form `<method>` con CSRF token e lo
    invia. Se il JS non e` disponibile, il fallback e` un semplice link
    GET (a quel punto la view dovrebbe gestire la conferma server-side).
    """

    return _build_link(
        url,
        label,
        base_class="velora-link velora-link-delete",
        extra_class=extra_class,
        title=title,
        disabled=disabled,
        extra_attrs={
            "data-velora-component": "confirm",
            "data-confirm-message": confirm_message,
            "data-confirm-method": method.lower(),
        },
    )


@register.simple_tag
def velora_btn_link(
    url: str = "",
    label: str = "",
    variant: str = "secondary",
    title: str = "",
    target: str = "",
    rel: str = "",
    disabled: bool = False,
    extra_class: str = "",
) -> SafeString:
    """Link stilizzato come bottone (riusa `velora-btn--<variant>` da M2).

    Variant valide: `primary`, `secondary`. Le varianti `success`/`danger`
    saranno aggiunte in M5.
    """

    if variant not in {"primary", "secondary"}:
        variant = "secondary"
    classes = f"velora-btn velora-btn--{variant}"
    return _build_link(
        url,
        label,
        base_class=classes,
        extra_class=extra_class,
        title=title,
        target=target,
        rel=rel,
        disabled=disabled,
    )


# =============================================================================
# v0.2 - Fase 10
# =============================================================================


@register.simple_tag
def velora_settings_link(
    url: str = "",
    label: str = "Impostazioni",
    title: str = "",
    target: str = "",
    rel: str = "",
    disabled: bool = False,
    extra_class: str = "",
) -> SafeString:
    """Link "configurazioni / settings" (verde). Stessa firma di action_link
    ma stile differente; nasce per icone a forma di ingranaggio nei detail.
    """

    return _build_link(
        url,
        label,
        base_class="velora-link velora-link-settings",
        extra_class=extra_class,
        title=title,
        target=target,
        rel=rel,
        disabled=disabled,
    )


@register.simple_tag
def velora_toggle_link(
    target: str = "",
    label_show: str = "Mostra",
    label_hide: str = "Nascondi",
    initial_state: str = "hidden",
    title: str = "",
    extra_class: str = "",
) -> SafeString:
    """Link che mostra/nasconde un blocco target e alterna il proprio label.

    Args:
        target: selettore CSS dell'elemento da togglare (es. "#dettagli").
            Se vuoto, il tag ritorna stringa vuota (no markup).
        label_show: testo del link quando il target e` nascosto.
        label_hide: testo del link quando il target e` visibile.
        initial_state: "hidden" (default, label_show iniziale) oppure
            "shown".

    Il componente JS `toggle-link` (vedi `js/src/components/toggle.js`)
    intercetta il click, commuta una classe `is-toggled-hidden` sul target
    e aggiorna il testo con `data-toggle-label-*`.
    """

    if not target:
        return mark_safe("")
    is_hidden = initial_state != "shown"
    initial_label = label_show if is_hidden else label_hide
    classes = f"velora-link velora-link-toggle{' is-active' if not is_hidden else ''}"
    if extra_class:
        classes = f"{classes} {extra_class}"
    return mark_safe(
        format_html(
            '<a href="#" class="{}" '
            'data-velora-component="toggle-link" '
            'data-toggle-target="{}" '
            'data-toggle-label-show="{}" '
            'data-toggle-label-hide="{}" '
            'data-toggle-state="{}"'
            '{}>{}</a>',
            classes,
            target,
            label_show,
            label_hide,
            "hidden" if is_hidden else "shown",
            mark_safe(_attr("title", title)),
            initial_label,
        )
    )


@register.simple_tag
def velora_copy_link(
    value: str = "",
    target: str = "",
    label: str = "Copia",
    label_copied: str = "Copiato",
    title: str = "",
    extra_class: str = "",
) -> SafeString:
    """Link copy-to-clipboard.

    Almeno uno fra `value` (testo statico) e `target` (selettore CSS verso
    elemento da cui leggere `.value` o `.textContent`) deve essere presente,
    altrimenti il tag non emette markup.

    Il componente JS `copy-link` (vedi `js/src/components/copy.js`):
      - su click esegue `navigator.clipboard.writeText(...)`
      - mostra un toast Velora di successo con `label_copied`
      - sostituisce temporaneamente il label del link con `label_copied`
        per ~1.5s, poi torna a `label`
    """

    if not value and not target:
        return mark_safe("")
    classes = "velora-link velora-link-copy"
    if extra_class:
        classes = f"{classes} {extra_class}"
    return mark_safe(
        format_html(
            '<a href="#" class="{}" '
            'data-velora-component="copy-link" '
            'data-copy-value="{}" '
            'data-copy-target="{}" '
            'data-copy-label="{}" '
            'data-copy-label-copied="{}"'
            '{}>{}</a>',
            classes,
            value,
            target,
            label,
            label_copied,
            mark_safe(_attr("title", title)),
            label,
        )
    )


def _normalize_dropdown_items(items: Any) -> list[dict[str, str]]:
    """Filtra i sub-item del drop_down: occorrono `label` e `url`.

    Item validi accettano `label`, `url`, `icon` (default ""), `extra_class`
    (default "").
    """

    if not items:
        return []
    out: list[dict[str, str]] = []
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
                "extra_class": raw.get("extra_class", ""),
            }
        )
    return out


def _render_dropdown(
    *,
    label: str,
    items: list[dict[str, str]],
    base_class: str,
    align: str,
    extra_class: str,
    title: str,
) -> SafeString:
    """Render condiviso fra `velora_drop_down_link` e `velora_drop_down_button`."""

    if not items:
        return mark_safe("")
    if align not in {"left", "right"}:
        align = "left"
    classes = f"velora-dropdown {extra_class}".strip()
    item_lines: list[str] = []
    for sub in items:
        link_class = "velora-dropdown__link"
        if sub["extra_class"]:
            link_class = f"{link_class} {sub['extra_class']}"
        icon_html = (
            format_html(
                '<span class="velora-dropdown__icon velora-icon velora-icon--{}" aria-hidden="true"></span>',
                sub["icon"],
            )
            if sub["icon"]
            else ""
        )
        item_lines.append(
            format_html(
                '<li role="none"><a role="menuitem" class="{}" href="{}">{}<span>{}</span></a></li>',
                link_class,
                sub["url"],
                icon_html,
                sub["label"],
            )
        )
    items_html = mark_safe("".join(item_lines))
    return mark_safe(
        format_html(
            '<div class="{}" data-velora-component="dropdown" data-velora-dropdown-align="{}">'
            '<button type="button" class="{}" aria-haspopup="true" aria-expanded="false"{}>'
            '<span class="velora-dropdown__label">{}</span>'
            '<span class="velora-dropdown__caret" aria-hidden="true">&#9660;</span>'
            "</button>"
            '<ul class="velora-dropdown__panel" role="menu">{}</ul>'
            "</div>",
            classes,
            align,
            base_class,
            mark_safe(_attr("title", title)),
            label,
            items_html,
        )
    )


@register.simple_tag
def velora_drop_down_link(
    label: str = "",
    items: Any = None,
    align: str = "left",
    title: str = "",
    extra_class: str = "",
) -> SafeString:
    """Link con dropdown: trigger stilizzato come link (sobrio) + pannello
    di voci. Item senza `label` o `url` vengono scartati. Se la lista
    risultante e` vuota il tag non emette nulla.

    Esempio:
        {% velora_drop_down_link label="Altre azioni" items=actions %}
    """

    return _render_dropdown(
        label=label,
        items=_normalize_dropdown_items(items),
        base_class="velora-link velora-link-dropdown",
        align=align,
        extra_class=extra_class,
        title=title,
    )


@register.simple_tag
def velora_drop_down_button(
    label: str = "",
    items: Any = None,
    variant: str = "secondary",
    align: str = "left",
    title: str = "",
    extra_class: str = "",
) -> SafeString:
    """Bottone con dropdown: trigger stilizzato come bottone (`velora-btn`)
    + pannello di voci. `variant` valide: `primary`, `secondary`.
    """

    if variant not in {"primary", "secondary"}:
        variant = "secondary"
    base_class = f"velora-btn velora-btn--{variant}"
    return _render_dropdown(
        label=label,
        items=_normalize_dropdown_items(items),
        base_class=base_class,
        align=align,
        extra_class=extra_class,
        title=title,
    )


@register.simple_tag
def velora_open_dialog_action_link(
    label: str = "",
    target: str = "",
    url: str = "",
    title: str = "",
    extra_class: str = "",
    size: str = "md",
    dialog_title: str = "",
) -> SafeString:
    """Link che apre un dialog modale.

    Due modalita`:
      - **Inline** (`target="#dialog-id"`): il dialog e` gia` nel DOM e
        viene mostrato immediatamente dal componente JS `dialog`.
      - **Remote** (`url="/path/to/fragment"`): il componente JS scarica
        il frammento HTML dalla URL e lo inietta in un dialog generato
        al volo.

    Almeno uno fra `target` e `url` deve essere presente; altrimenti il
    tag ritorna stringa vuota.

    `size` valide: "sm", "md", "lg". Sconosciuta -> fallback "md".
    """

    if not target and not url:
        return mark_safe("")
    if size not in {"sm", "md", "lg"}:
        size = "md"
    classes = "velora-link velora-link-action velora-link-dialog"
    if extra_class:
        classes = f"{classes} {extra_class}"
    return mark_safe(
        format_html(
            '<a href="{}" class="{}" '
            'data-velora-component="dialog" '
            'data-dialog-target="{}" '
            'data-dialog-url="{}" '
            'data-dialog-size="{}" '
            'data-dialog-title="{}"'
            '{}>{}</a>',
            url or "#",
            classes,
            target,
            url,
            size,
            dialog_title,
            mark_safe(_attr("title", title)),
            label,
        )
    )
