"""Test per `velora_data` (tabella + paginazione) e `velora_links` (4 link).

M4 / Fase 6 del piano. Coperto:

  velora_table:
    - rendering basic con headers list e rows list
    - rows come dict (richiede `key` negli headers)
    - empty_message + colspan quando rows vuoto
    - escape applicato di default (Django autoescape) sui valori cella
    - allineamento (align=right/center) propagato sia su th che td

  velora_pagination:
    - nav nascosta se num_pages <= 1
    - pagina corrente marcata is-current con aria-current=page
    - prev/next disabilitati ai bordi
    - finestra di pagine con `…` per salti
    - querystring conserva altri parametri di base_url
    - accetta sia oggetto Page Django sia dict

  velora_action_link / nav / btn:
    - classi CSS attese
    - escape su URL e label
    - disabled -> is-disabled, aria-disabled, href=#

  velora_delete_link:
    - aggiunge data-velora-component="confirm"
    - data-confirm-message custom rispettato
    - data-confirm-method lowercase

  velora_btn_link:
    - variant unknown -> secondary
"""

from __future__ import annotations

from django.template import Context, Template


def render(source: str, context: dict | None = None) -> str:
    return Template(source).render(Context(context or {}))


# -- velora_table ------------------------------------------------------


def test_table_renders_headers_and_rows():
    html = render(
        "{% load velora_data %}{% velora_table headers=h rows=r %}",
        {
            "h": ["Nome", "Email"],
            "r": [["Mario", "m@x.it"], ["Luca", "l@y.it"]],
        },
    )
    assert "<table" in html
    assert "Nome" in html
    assert "Email" in html
    assert "Mario" in html
    assert "l@y.it" in html
    assert html.count("<tr") >= 3  # 1 thead + 2 tbody


def test_table_dict_rows_with_keys():
    html = render(
        "{% load velora_data %}{% velora_table headers=h rows=r %}",
        {
            "h": [{"key": "name", "label": "Nome"}, {"key": "age", "label": "Eta"}],
            "r": [{"name": "Mario", "age": 30}, {"name": "Luca", "age": 25}],
        },
    )
    assert "Mario" in html
    assert "30" in html


def test_table_empty_message_with_colspan():
    html = render(
        "{% load velora_data %}{% velora_table headers=h rows=r empty_message='Vuoto' %}",
        {"h": ["A", "B", "C"], "r": []},
    )
    assert "Vuoto" in html
    assert 'colspan="3"' in html


def test_table_escapes_cell_values():
    html = render(
        "{% load velora_data %}{% velora_table headers=h rows=r %}",
        {"h": ["X"], "r": [["<script>alert(1)</script>"]]},
    )
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_table_align_propagates_to_th_and_td():
    html = render(
        "{% load velora_data %}{% velora_table headers=h rows=r %}",
        {
            "h": [{"label": "Tot", "align": "right", "key": "tot"}],
            "r": [{"tot": 99}],
        },
    )
    assert html.count("velora-table__cell--right") == 2  # th + td


# -- velora_pagination -------------------------------------------------


def test_pagination_hidden_when_one_page():
    html = render(
        "{% load velora_data %}{% velora_pagination page=p %}",
        {"p": {"number": 1, "num_pages": 1}},
    )
    # Nessuna nav resa
    assert "velora-pagination" not in html


def test_pagination_marks_current_page():
    html = render(
        "{% load velora_data %}{% velora_pagination page=p base_url='/list/' %}",
        {"p": {"number": 3, "num_pages": 5}},
    )
    assert 'aria-current="page"' in html
    assert "is-current" in html
    # La pagina corrente e` uno <span> (non un <a>): cerco il numero dentro
    # il marker is-current. Le altre pagine devono avere il link con
    # ?page=N preservando base_url.
    assert ">3</span>" in html
    assert "/list/?page=2" in html
    assert "/list/?page=4" in html


def test_pagination_prev_disabled_on_first():
    html = render(
        "{% load velora_data %}{% velora_pagination page=p %}",
        {"p": {"number": 1, "num_pages": 5}},
    )
    assert "velora-pagination__step--prev is-disabled" in html
    assert "velora-pagination__step--next" in html
    assert "is-disabled\">Successivo" not in html


def test_pagination_next_disabled_on_last():
    html = render(
        "{% load velora_data %}{% velora_pagination page=p %}",
        {"p": {"number": 5, "num_pages": 5}},
    )
    assert "velora-pagination__step--next is-disabled" in html


def test_pagination_window_includes_gap():
    html = render(
        "{% load velora_data %}{% velora_pagination page=p %}",
        {"p": {"number": 10, "num_pages": 20}},
    )
    assert "velora-pagination__gap" in html


def test_pagination_preserves_other_query_params():
    html = render(
        "{% load velora_data %}{% velora_pagination page=p base_url=u %}",
        {
            "p": {"number": 2, "num_pages": 4},
            "u": "/items/?status=open&sort=name",
        },
    )
    # I link delle pagine devono mantenere status e sort
    assert "status=open" in html
    assert "sort=name" in html
    assert "page=2" in html or "page=3" in html


def test_pagination_accepts_django_page_object():
    """Anatra-tipato: simulo un oggetto Page con attributi/metodi attesi."""

    class _Paginator:
        num_pages = 4

    class _Page:
        paginator = _Paginator()
        number = 2

        def has_previous(self):
            return True

        def has_next(self):
            return True

        def previous_page_number(self):
            return 1

        def next_page_number(self):
            return 3

    html = render(
        "{% load velora_data %}{% velora_pagination page=p base_url='/' %}",
        {"p": _Page()},
    )
    assert "velora-pagination" in html
    # corrente = pagina 2 -> <span>2</span>, prev/next sono pagine 1 e 3
    assert ">2</span>" in html
    assert "/?page=1" in html
    assert "/?page=3" in html


# -- velora_action_link ------------------------------------------------


def test_action_link_renders_orange_class():
    html = render(
        "{% load velora_links %}{% velora_action_link url='/edit/' label='Modifica' %}"
    )
    assert "velora-link-action" in html
    assert 'href="/edit/"' in html
    assert "Modifica" in html


def test_action_link_escapes_label():
    html = render(
        "{% load velora_links %}{% velora_action_link url='/x/' label=l %}",
        {"l": "<b>Hack</b>"},
    )
    assert "<b>Hack</b>" not in html
    assert "&lt;b&gt;Hack" in html


def test_action_link_disabled_state():
    html = render(
        "{% load velora_links %}{% velora_action_link url='/x/' label='X' disabled=True %}"
    )
    assert "is-disabled" in html
    assert 'aria-disabled="true"' in html
    assert 'href="#"' in html


def test_action_link_target_blank_adds_rel_noopener():
    html = render(
        "{% load velora_links %}{% velora_action_link url='https://x' label='X' target='_blank' %}"
    )
    assert 'target="_blank"' in html
    assert "noopener noreferrer" in html


# -- velora_nav_link ---------------------------------------------------


def test_nav_link_renders_blue_class():
    html = render(
        "{% load velora_links %}{% velora_nav_link url='/d/1/' label='Dettagli' %}"
    )
    assert "velora-link-nav" in html
    assert "Dettagli" in html


# -- velora_delete_link ------------------------------------------------


def test_delete_link_default_label_and_attrs():
    html = render(
        "{% load velora_links %}{% velora_delete_link url='/del/1/' %}"
    )
    assert "velora-link-delete" in html
    assert "Elimina" in html  # label di default
    assert 'data-velora-component="confirm"' in html
    assert 'data-confirm-message="Confermi l&#x27;eliminazione?"' in html or \
           "Confermi l'eliminazione?" in html
    assert 'data-confirm-method="post"' in html


def test_delete_link_custom_message_and_method():
    html = render(
        "{% load velora_links %}"
        "{% velora_delete_link url='/del/1/' confirm_message='Sicuro?' method='POST' %}"
    )
    assert 'data-confirm-message="Sicuro?"' in html
    assert 'data-confirm-method="post"' in html


# -- velora_btn_link ---------------------------------------------------


def test_btn_link_primary_variant():
    html = render(
        "{% load velora_links %}{% velora_btn_link url='/n/' label='Nuovo' variant='primary' %}"
    )
    assert "velora-btn velora-btn--primary" in html


def test_btn_link_unknown_variant_falls_back_to_secondary():
    html = render(
        "{% load velora_links %}{% velora_btn_link url='/n/' label='X' variant='alien' %}"
    )
    assert "velora-btn--secondary" in html
    assert "velora-btn--alien" not in html
