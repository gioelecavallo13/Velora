#!/usr/bin/env python3
"""Rigenera lo showcase con campioni solo visivi + barra classi (vedi index.html).

Non eseguire due volte sullo stesso file senza ripristinare da git: le sostituzioni
non sono idempotenti (es. doppio wrap della galleria).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "showcase/templates/showcase/index.html"

TITLE_LABELS = {
    "Datepicker e Datetimepicker": (
        '<div class="showcase-sample__label">'
        "<code>.velora-form-row.velora-form-row--datepicker</code> · "
        "<code>.velora-datepicker</code> · "
        "<code>.velora-form-row.velora-form-row--datetimepicker</code>"
        "</div>"
    ),
    "Multiselect (chip + dropdown)": (
        '<div class="showcase-sample__label">'
        "<code>.velora-form-row.velora-form-row--multiselect</code> · "
        "<code>.velora-multiselect</code>"
        "</div>"
    ),
    "Autocomplete (locale e remoto)": (
        '<div class="showcase-sample__label">'
        "<code>.velora-form-row--autocomplete</code> · "
        "<code>.velora-autocomplete</code> · "
        "<code>.velora-autocomplete--remote</code>"
        "</div>"
    ),
    "Image preview, rating, timer": (
        '<div class="showcase-sample__label">'
        "<code>.velora-form-row--image-preview</code> · "
        "<code>.velora-image-preview</code> · "
        "<code>.velora-form-row--rating</code> · "
        "<code>.velora-rating</code> · "
        "<code>.velora-form-row--timer</code> · "
        "<code>.velora-timer</code>"
        "</div>"
    ),
    "Redactor (toolbar + textarea)": (
        '<div class="showcase-sample__label">'
        "<code>.velora-form-row--redactor</code> · <code>.velora-redactor</code>"
        "</div>"
    ),
    "Tabella editabile + bulk actions": (
        '<div class="showcase-sample__label">'
        "<code>.velora-bulk-toolbar</code> · "
        "<code>.velora-table.velora-table--selectable</code>"
        "</div>"
    ),
    "Schema riga con form-in-cell": (
        '<div class="showcase-sample__label">'
        "<code>.velora-cell-form</code> · <code>.velora-cell-form__input</code> · "
        "<code>__select</code> · <code>__checkbox</code> · <code>__onoff</code>"
        "</div>"
        '<p class="showcase-sample__note">{% trans "Struttura dati form_in_cell:" %} '
        "<code>AGENTS.md</code> ({% trans \"velora_data / velora_table\" %}).</p>"
    ),
    "Varianti colore": (
        '<div class="showcase-sample__label">'
        "<code>.velora-checkbox</code> · <code>.velora-checkbox--default|primary|info|success|danger</code>"
        "</div>"
    ),
    "Radio group": (
        '<div class="showcase-sample__label">'
        "<code>.velora-checkbox</code> ({% trans \"input type=radio\" %})"
        "</div>"
    ),
}

# Ordine: ogni blocco <div class="showcase-sample"> che apre con __preview (no __label già presente)
AUTO_LABELS = [
    '<div class="showcase-sample__label"><code>.velora-header</code> · <code>.velora-header__*</code></div>',
    '<div class="showcase-sample__label"><code>.velora-title-bar</code> · <code>.velora-btn</code></div>',
    '<div class="showcase-sample__label"><code>.velora-form-row.velora-form-row--text</code> · <code>.velora-form-row__input</code></div>',
    '<div class="showcase-sample__label"><code>.velora-form-row--textarea</code> · <code>.velora-form-row__textarea</code></div>',
    '<div class="showcase-sample__label"><code>.velora-form-row--select</code> · <code>.velora-form-row__select</code></div>',
    '<div class="showcase-sample__label"><code>.velora-form-row--checkbox</code> · <code>.velora-form-row--onoff</code></div>',
    '<div class="showcase-sample__label"><code>.velora-form-row--radio</code> · <code>.velora-form-row__radio-list</code></div>',
    '<div class="showcase-sample__label"><code>.velora-form-row--file</code></div>',
    '<div class="showcase-sample__label"><code>.velora-form-row--error</code></div>',
    '<div class="showcase-sample__label"><code>.velora-search-box</code> · <code>.velora-fields-separator</code></div>',
    '<div class="showcase-sample__label"><code>.velora-table-wrapper</code> · <code>.velora-table</code> · <code>.velora-pagination</code></div>',
    '<div class="showcase-sample__label"><code>.velora-link-action</code> · <code>.velora-link-nav</code> · <code>.velora-link-delete</code></div>',
    '<div class="showcase-sample__label"><code>.velora-btn</code> · <code>.velora-btn--primary</code> · <code>.velora-btn--secondary</code></div>',
    '<div class="showcase-sample__label"><code>.velora-alert</code> · <code>.velora-alert--success|error|warning|info</code></div>',
    '<div class="showcase-sample__label"><code>.velora-label</code> · <code>.velora-label--*</code></div>',
    '<div class="showcase-sample__label"><code>.velora-toast</code> ({% trans \"API JS\" %} Velora.toast.*)</div>',
    '<div class="showcase-sample__label"><code>.velora-toast</code> ({% trans \"django.contrib.messages\" %})</div>',
    '<div class="showcase-sample__label"><code>.velora-breadcrumb</code> · <code>.velora-breadcrumb__*</code></div>',
    '<div class="showcase-sample__label"><code>.velora-submenu</code> · <code>.velora-submenu__*</code></div>',
    '<div class="showcase-sample__label"><code>.velora-link-dropdown</code> · pannello nello <code>.velora-header</code></div>',
    '<div class="showcase-sample__label"><code>.velora-link-settings</code> · toggle · copy · confirm</div>',
    '<div class="showcase-sample__label"><code>[data-velora-component=&quot;tooltip&quot;]</code></div>',
    '<div class="showcase-sample__label"><code>.velora-dialog</code> · <code>.velora-dialog__*</code></div>',
    '<div class="showcase-sample__label"><code>.velora-progress</code> · <code>.velora-progress__track</code></div>',
    '<div class="showcase-sample__label"><code>.velora-progress-steps</code> · <code>.velora-progress-steps__*</code></div>',
    '<div class="showcase-sample__label"><code>.velora-progress-xy</code> · <code>.velora-progress-xy__*</code></div>',
    '<div class="showcase-sample__label"><code>.velora-table-wrapper</code> · <code>.velora-table</code> · <code>.velora-chart</code> · <code>canvas</code></div>',
    '<div class="showcase-sample__label"><code>.velora-icon</code> · <code>.velora-icon--*</code></div>',
    '<div class="showcase-sample__label"><code>[data-velora-theme]</code> · <code>.velora-logo</code> · <code>.velora-satisfaction</code></div>',
]


def replace_title_div(s: str) -> str:
    def repl(m: re.Match[str]) -> str:
        title = m.group(1).strip()
        if title in TITLE_LABELS:
            return TITLE_LABELS[title]
        return (
            f'<div class="showcase-sample__label"><code>{title}</code></div>'
        )

    return re.sub(
        r'<div class="showcase-demo__title">(.*?)</div>\s*',
        repl,
        s,
        flags=re.DOTALL,
    )


def main() -> None:
    s = PATH.read_text(encoding="utf-8")

    s = replace_title_div(s)

    s = re.sub(
        r"\s*<pre class=\"showcase-demo__code\">.*?</pre>",
        "",
        s,
        flags=re.DOTALL,
    )

    repls = [
        (
            '<div class="showcase-demo showcase-demo--stacked showcase-demo--layout-header">',
            '<div class="showcase-sample showcase-sample--clip">',
        ),
        (
            '<div class="showcase-demo showcase-demo--layout-header">',
            '<div class="showcase-sample showcase-sample--clip">',
        ),
        ('<div class="showcase-demo showcase-demo--stacked">', '<div class="showcase-sample">'),
        ('<div class="showcase-demo">', '<div class="showcase-sample">'),
    ]
    for old, new in repls:
        s = s.replace(old, new)

    s = s.replace(
        'class="showcase-demo__live showcase-demo__live--header"',
        'class="showcase-sample__preview showcase-sample__preview--header"',
    )
    s = s.replace(
        'class="showcase-demo__live showcase-demo__live--title-bar"',
        'class="showcase-sample__preview showcase-sample__preview--title-bar"',
    )
    s = s.replace('class="showcase-demo__live"', 'class="showcase-sample__preview"')
    s = s.replace('class="showcase-demo__render"', 'class="showcase-sample__preview"')

    idx = 0

    def inject_preview(m: re.Match[str]) -> str:
        nonlocal idx
        if idx >= len(AUTO_LABELS):
            raise SystemExit(f"Troppi blocchi preview: servono più etichette (idx={idx})")
        label = AUTO_LABELS[idx]
        idx += 1
        return m.group(1) + label + "\n        " + m.group(2)

    # Inserisce etichetta solo se subito dopo l'apertura showcase-sample compare __preview
    s = re.sub(
        r'(<div class="showcase-sample(?: showcase-sample--clip)?">\s*)'
        r'(<div class="showcase-sample__preview)',
        inject_preview,
        s,
    )

    if idx != len(AUTO_LABELS):
        raise SystemExit(
            f"Etichette AUTO_LABELS: usate {idx}, definite {len(AUTO_LABELS)}"
        )

    # Gallery Ionicons: avvolgi in sample + label
    needle = '{% velora_ionicons_gallery search_input_id="showcase-ionicons-search"'
    pos = s.find(needle)
    if pos != -1:
        before = s.rfind("<h3", 0, pos)
        after_line = s.find("\n", s.find("%}", pos) + 2)
        # trova fine tag gallery (prima riga dopo %})
        end_gallery = s.find("%}", pos) + 2
        block = s[pos:end_gallery]
        wrapped = (
            '    <div class="showcase-sample">\n'
            '        <div class="showcase-sample__label">'
            "<code>.velora-ionicons-gallery</code> · <code>.velora-ionicons-gallery__*</code>"
            "</div>\n"
            f"        <div class=\"showcase-sample__preview\">\n            {block}\n"
            "        </div>\n    </div>"
        )
        s = s[:pos] + wrapped + s[end_gallery:]

    PATH.write_text(s, encoding="utf-8")
    print(f"[showcase_visual_labels] aggiornato {PATH}")


if __name__ == "__main__":
    main()
