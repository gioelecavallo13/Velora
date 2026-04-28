"""Default e helper di accesso alle settings del pacchetto velora_ui.

Velora UI consuma alcune voci da `django.conf.settings` per personalizzare
header e branding. Per non costringere il progetto host a definirle tutte
manualmente, qui dichiariamo i `DEFAULTS` e l'helper `get_setting()` che
restituisce il valore eventualmente ridefinito nel settings del progetto host
oppure il default.

Convenzione: tutte le chiavi pubbliche del pacchetto iniziano con il prefisso
``VELORA_``. Aggiungere una nuova voce significa:

  1. inserirla in `DEFAULTS` con il valore di default
  2. documentarla nel README sezione "Settings"
  3. eventualmente esporla via context processor se serve in template

Le voci dichiarate qui in v0.1 (M2):

  - ``VELORA_HEADER_APP_NAME`` (str): nome dell'applicazione mostrato accanto
    al logo nell'header. Default: "Velora UI".
  - ``VELORA_HEADER_APP_ICON_URL`` (str | None): URL del logo dell'app
    visualizzato nell'header. Se ``None`` (default), il brand mostra solo il
    nome.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings as django_settings


DEFAULTS: dict[str, Any] = {
    "VELORA_HEADER_APP_NAME": "Velora UI",
    "VELORA_HEADER_APP_ICON_URL": None,
}


def get_setting(name: str) -> Any:
    """Ritorna il valore della setting `name` con fallback ai default.

    Se la setting non e` ne` definita nel progetto host ne` in `DEFAULTS`,
    viene sollevato `KeyError`: questo segnala un uso improprio (chiavi che
    non esistono nel pacchetto) anziche` ritornare silenziosamente `None`.
    """

    if hasattr(django_settings, name):
        return getattr(django_settings, name)
    if name in DEFAULTS:
        return DEFAULTS[name]
    raise KeyError(f"Velora UI setting sconosciuta: {name!r}")
