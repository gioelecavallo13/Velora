"""Template tag `{% velora_assets %}`.

Inietta il bundle CSS+JS di Velora UI nel template.
Da usare nel `<head>` (oppure prima di `</body>` se si preferisce caricamento
non bloccante; in v0.1 lo posizioniamo nel head per coerenza con i file di
showcase).

Esempio uso::

    {% load velora_assets %}
    <!doctype html>
    <html>
      <head>
        {% velora_assets %}
      </head>
      ...
    </html>

Le URL sono risolte tramite `static()` in modo da rispettare `STATIC_URL`,
storage backend (whitenoise, S3) e qualunque altro hook configurato.
"""

from __future__ import annotations

from django import template
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


@register.simple_tag
def velora_assets() -> SafeString:
    """Restituisce i tag <link> e <script> per CSS e JS di Velora UI."""

    css_tag = format_html(
        '<link rel="stylesheet" href="{}" data-velora-asset="css">',
        static("velora_ui/css/velora.css"),
    )
    js_tag = format_html(
        '<script type="module" src="{}" data-velora-asset="js"></script>',
        static("velora_ui/js/velora.js"),
    )
    return mark_safe(f"{css_tag}\n    {js_tag}")
