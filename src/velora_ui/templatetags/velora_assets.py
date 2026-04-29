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

Comportamento URL:

- Con ``VELORA_ASSETS_BASE_URL`` vuota (default), le URL sono risolte tramite
  ``static()`` come da ``STATIC_URL`` e storage configurato.
- Con base valorizzata, dev'essere il prefisso HTTPS di una cartella GitHub
  ``.../releases/download/vX.Y.Z/``; i nomi file sono quelli della release
  (``velora-{versione}.min.css`` e JS core o full). Vietati host diversi da
  ``github.com`` e CDN terzi.
"""

from __future__ import annotations

from urllib.parse import urlparse

from django import template
from django.core.exceptions import ImproperlyConfigured
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

from velora_ui import __version__
from velora_ui.settings import get_setting

register = template.Library()


def _normalize_release_base_url(raw: str) -> str:
    """Valida e normalizza il prefisso Release GitHub. Ritorna URL con trailing slash."""

    url = (raw or "").strip()
    if not url:
        return ""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ImproperlyConfigured(
            "VELORA_ASSETS_BASE_URL deve usare il solo scheme https "
            "(distribuzione asset documentata solo via GitHub Releases)."
        )
    host = (parsed.netloc or "").lower()
    if "github.com" not in host:
        raise ImproperlyConfigured(
            "VELORA_ASSETS_BASE_URL deve puntare a github.com; "
            "CDN o host terzi non sono supportati per questa setting."
        )
    path = parsed.path or ""
    if "/releases/download/v" not in path:
        raise ImproperlyConfigured(
            "VELORA_ASSETS_BASE_URL deve includere il path "
            "…/releases/download/vX.Y.Z/ della GitHub Release."
        )
    return url.rstrip("/") + "/"


@register.simple_tag
def velora_assets() -> SafeString:
    """Restituisce i tag <link> e <script> per CSS e JS di Velora UI."""

    raw_base = get_setting("VELORA_ASSETS_BASE_URL")
    base = _normalize_release_base_url(raw_base) if (raw_base or "").strip() else ""

    if base:
        use_full = bool(get_setting("VELORA_ASSETS_JS_FULL"))
        ver = __version__
        css_href = f"{base}velora-{ver}.min.css"
        js_name = f"velora-{ver}.full.min.js" if use_full else f"velora-{ver}.min.js"
        js_src = f"{base}{js_name}"
    else:
        css_href = static("velora_ui/css/velora.css")
        js_src = static("velora_ui/js/velora.js")

    css_tag = format_html(
        '<link rel="stylesheet" href="{}" data-velora-asset="css">',
        css_href,
    )
    js_tag = format_html(
        '<script type="module" src="{}" data-velora-asset="js"></script>',
        js_src,
    )
    return mark_safe(f"{css_tag}\n    {js_tag}")
