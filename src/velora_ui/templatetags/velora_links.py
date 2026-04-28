"""Link template tag essenziali (M4 - Fase 6 del piano).

Espone i 4 link base usati per popolare la colonna "azioni" delle tabelle e
le aree di navigazione di una pagina admin:

  - {% velora_action_link  url=... label=... %}  -> azione "principale" arancio
  - {% velora_nav_link     url=... label=... %}  -> link di navigazione blu
  - {% velora_delete_link  url=... %}            -> azione distruttiva rossa
  - {% velora_btn_link     url=... label=... %}  -> bottone-link generico

I tipi avanzati (`toggle_link`, `copy_to_clipboard_link`, `settings_link`,
`open_dialog_action_link`, `drop_down_link`, `submenu`) sono rinviati a v0.2
(vedi piano "Cosa NON entra in v0.1").

Convenzioni comuni:
  - Tutti i tag accettano `extra_class`, `target`, `rel`, `title`, `disabled`.
  - L'output e` SafeString.
  - Per evitare XSS i parametri stringa passano comunque attraverso
    `escape()` -- non costruiamo HTML grezzo da input utente.
"""

from __future__ import annotations

from typing import Any

from django import template
from django.utils.html import escape, format_html
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
