"""Script Python eseguito dentro il container effimero da
``tools/validation_gate_dev.sh``: simula un consumer della wheel velora-ui.

Configura un Django minimo *senza* il progetto host del repo, carica un
template che usa 9 componenti pubblici e verifica che ognuno produca il
proprio marker CSS distintivo. Verifica inoltre che app config, context
processor, widget custom e versione siano importabili dalla wheel.
"""

from __future__ import annotations

import django
from django.conf import settings

settings.configure(
    DEBUG=True,
    INSTALLED_APPS=["velora_ui"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "velora_ui.context_processors.header_defaults",
                ],
            },
        }
    ],
    STATIC_URL="/static/",
    USE_TZ=True,
    SECRET_KEY="test-only",
)
django.setup()

from django.template import Context, Template  # noqa: E402

TEMPLATE_STR = """
{% load velora_layout velora_forms velora_data velora_links velora_feedback %}

{% velora_form_row type="text" name="email" label="Email" %}
{% velora_form_row type="select" name="role" label="Ruolo" choices=role_choices %}
{% velora_search_box name="q" placeholder="Cerca..." %}
{% velora_table headers=table_headers rows=table_rows %}
{% velora_action_link url="/edit/" label="Modifica" %}
{% velora_nav_link url="/detail/" label="Dettaglio" %}
{% velora_delete_link url="/delete/" %}
{% velora_alert variant="success" message="Salvato" dismissible=True %}
{% velora_label variant="warning" text="In revisione" %}
"""

ctx = Context(
    {
        "role_choices": [("admin", "Amministratore"), ("user", "Utente")],
        "table_headers": [
            {"key": "name", "label": "Nome"},
            {"key": "email", "label": "Email"},
        ],
        "table_rows": [{"name": "Mario", "email": "mario@x.it"}],
    }
)

output = Template(TEMPLATE_STR).render(ctx)

REQUIRED_MARKERS = {
    "velora_form_row[text]": "velora-form-row",
    "velora_form_row[select]": "<select",
    "velora_search_box": "velora-search-box",
    "velora_table": "velora-table",
    "velora_action_link": "velora-link-action",
    "velora_nav_link": "velora-link-nav",
    "velora_delete_link": "velora-link-delete",
    "velora_alert": "velora-alert",
    "velora_label": "velora-label",
}

missing = [name for name, marker in REQUIRED_MARKERS.items() if marker not in output]
if missing:
    print(f"[validation-gate-dev] MARKER MANCANTI: {missing}")
    print("--- output (1500 char) ---")
    print(output[:1500])
    raise SystemExit(1)

# Importabilita` di superficie pubblica del package
from velora_ui import __version__  # noqa: E402
from velora_ui.apps import VeloraUiConfig  # noqa: E402
from velora_ui.context_processors import header_defaults  # noqa: E402
from velora_ui.widgets import OnOffWidget  # noqa: E402

assert VeloraUiConfig.name == "velora_ui", VeloraUiConfig.name
assert callable(header_defaults), "header_defaults non callable"
assert OnOffWidget is not None, "OnOffWidget non importabile"
assert __version__, "velora_ui.__version__ vuoto"

print(
    f"[validation-gate-dev] OK: 9/9 marker presenti, "
    f"app config OK, version={__version__}"
)
