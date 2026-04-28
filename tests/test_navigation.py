"""Test della templatetag library `velora_navigation` (Fase 10).

Coperti:
  - velora_breadcrumb            (10.2)
  - velora_submenu               (10.4)
  - velora_progress_bar          (10.10)
  - velora_condensed_progress_breadcrumb (10.11)
  - velora_new_progress_bar      (10.12)
"""

from __future__ import annotations

from django.template import Context, Template


def render(source: str, context: dict | None = None) -> str:
    return Template(source).render(Context(context or {}))


# -- velora_breadcrumb (10.2) ---------------------------------------------


def test_breadcrumb_renders_links_and_current():
    html = render(
        "{% load velora_navigation %}{% velora_breadcrumb items=items %}",
        {
            "items": [
                {"label": "Home", "url": "/"},
                {"label": "Clienti", "url": "/clients/"},
                {"label": "Mario Rossi"},
            ]
        },
    )
    assert "velora-breadcrumb" in html
    assert 'href="/"' in html
    assert 'href="/clients/"' in html
    assert 'aria-current="page"' in html
    assert html.count('aria-current="page"') == 1
    assert "Mario Rossi" in html
    # last item: no <a>
    assert 'href="/last"' not in html


def test_breadcrumb_separator_default_and_custom():
    html_default = render(
        "{% load velora_navigation %}{% velora_breadcrumb items=items %}",
        {"items": [{"label": "A", "url": "/a"}, {"label": "B"}]},
    )
    assert "&rsaquo;" in html_default or "›" in html_default
    html_custom = render(
        "{% load velora_navigation %}{% velora_breadcrumb items=items separator='/' %}",
        {"items": [{"label": "A", "url": "/a"}, {"label": "B"}]},
    )
    assert "/" in html_custom


def test_breadcrumb_filters_malformed_items():
    html = render(
        "{% load velora_navigation %}{% velora_breadcrumb items=items %}",
        {
            "items": [
                {"label": "Ok", "url": "/ok"},
                "non-dict",
                {"url": "/no-label"},
                None,
                {"label": "Last"},
            ]
        },
    )
    assert "Ok" in html
    assert "Last" in html
    assert "non-dict" not in html
    assert "/no-label" not in html


def test_breadcrumb_empty_items_renders_nav_without_list():
    html = render(
        "{% load velora_navigation %}{% velora_breadcrumb items=items %}",
        {"items": []},
    )
    assert "velora-breadcrumb" in html
    assert "<ol" not in html


# -- velora_submenu (10.4) ------------------------------------------------


def test_submenu_renders_items_with_title():
    html = render(
        "{% load velora_navigation %}{% velora_submenu items=items title='Azioni' %}",
        {
            "items": [
                {"label": "Modifica", "url": "/edit/"},
                {"label": "Elimina", "url": "/del/", "active": True},
            ]
        },
    )
    assert "velora-submenu" in html
    assert "Azioni" in html
    assert 'href="/edit/"' in html
    assert "Modifica" in html
    assert "Elimina" in html
    assert "is-active" in html
    assert html.count("is-active") == 1
    assert 'aria-current="page"' in html


def test_submenu_no_title():
    html = render(
        "{% load velora_navigation %}{% velora_submenu items=items %}",
        {"items": [{"label": "X", "url": "/x"}]},
    )
    assert "velora-submenu" in html
    assert "velora-submenu__title" not in html


def test_submenu_empty_renders_nothing():
    html = render(
        "{% load velora_navigation %}{% velora_submenu items=items title='T' %}",
        {"items": []},
    )
    assert "velora-submenu" not in html


def test_submenu_filters_malformed():
    html = render(
        "{% load velora_navigation %}{% velora_submenu items=items %}",
        {
            "items": [
                {"label": "Ok", "url": "/ok"},
                {"label": "Senza URL"},
                {"url": "/senza-label"},
                "stringa",
            ]
        },
    )
    assert "Ok" in html
    assert "Senza URL" not in html
    assert "/senza-label" not in html


# -- velora_progress_bar (10.10) ------------------------------------------


def test_progress_bar_default_renders_role_progressbar():
    html = render(
        "{% load velora_navigation %}{% velora_progress_bar value=70 max=100 label='Caricamento' %}"
    )
    assert 'role="progressbar"' in html
    assert 'aria-valuenow="70"' in html
    assert 'aria-valuemax="100"' in html
    assert "Caricamento" in html
    assert "70%" in html
    assert "width: 70.00%;" in html
    assert "velora-progress--default" in html


def test_progress_bar_clamps_negative_and_over_max():
    html_neg = render("{% load velora_navigation %}{% velora_progress_bar value=-50 max=100 %}")
    assert 'aria-valuenow="0"' in html_neg
    assert "width: 0.00%;" in html_neg
    html_over = render("{% load velora_navigation %}{% velora_progress_bar value=200 max=100 %}")
    assert 'aria-valuenow="100"' in html_over
    assert "width: 100.00%;" in html_over


def test_progress_bar_zero_max_safe():
    html = render("{% load velora_navigation %}{% velora_progress_bar value=10 max=0 %}")
    assert "width: 0.00%;" in html


def test_progress_bar_variants():
    for v, expected in [
        ("success", "velora-progress--success"),
        ("warning", "velora-progress--warning"),
        ("danger", "velora-progress--danger"),
        ("info", "velora-progress--info"),
        ("xxx", "velora-progress--default"),
    ]:
        html = render(
            "{% load velora_navigation %}{% velora_progress_bar value=50 variant=v %}",
            {"v": v},
        )
        assert expected in html, f"variant {v}: expected {expected}"


def test_progress_bar_show_percent_false():
    html = render(
        "{% load velora_navigation %}{% velora_progress_bar value=42 show_percent=False %}"
    )
    assert "velora-progress__percent" not in html


def test_progress_bar_string_values_castable():
    html = render(
        "{% load velora_navigation %}{% velora_progress_bar value='30' max='60' %}"
    )
    assert 'aria-valuenow="50"' in html  # 30/60*100=50
    assert "width: 50.00%;" in html


# -- velora_condensed_progress_breadcrumb (10.11) -------------------------


def test_condensed_breadcrumb_renders_steps():
    html = render(
        "{% load velora_navigation %}{% velora_condensed_progress_breadcrumb steps=s current=2 %}",
        {"s": ["Anagrafica", "Indirizzo", "Conferma"]},
    )
    assert "velora-progress-steps" in html
    assert "Anagrafica" in html
    assert "Indirizzo" in html
    assert "Conferma" in html
    assert "is-done" in html
    assert "is-current" in html
    assert "is-upcoming" in html
    assert html.count("is-done") == 1
    assert html.count("is-current") == 1
    assert html.count("is-upcoming") == 1
    assert 'aria-current="step"' in html


def test_condensed_breadcrumb_dict_steps_and_url():
    html = render(
        "{% load velora_navigation %}{% velora_condensed_progress_breadcrumb steps=s current=3 %}",
        {
            "s": [
                {"label": "Step1", "url": "/s1"},
                {"label": "Step2", "url": "/s2"},
                {"label": "Step3"},
            ]
        },
    )
    # done: step1, step2 (have url) -> rendered as <a>
    assert 'href="/s1"' in html
    assert 'href="/s2"' in html
    assert "Step3" in html
    # current step (Step3) is NOT rendered as link
    assert html.count("velora-progress-steps__link") >= 3


def test_condensed_breadcrumb_clamps_current():
    # current oltre il numero di step -> ultimo
    html = render(
        "{% load velora_navigation %}{% velora_condensed_progress_breadcrumb steps=s current=99 %}",
        {"s": ["A", "B"]},
    )
    assert "is-current" in html
    # current=0 -> 1
    html2 = render(
        "{% load velora_navigation %}{% velora_condensed_progress_breadcrumb steps=s current=0 %}",
        {"s": ["A", "B"]},
    )
    assert "is-current" in html2
    assert "is-upcoming" in html2


def test_condensed_breadcrumb_empty_steps():
    html = render(
        "{% load velora_navigation %}{% velora_condensed_progress_breadcrumb steps=s current=1 %}",
        {"s": []},
    )
    assert "velora-progress-steps" not in html


def test_condensed_breadcrumb_filters_malformed():
    html = render(
        "{% load velora_navigation %}{% velora_condensed_progress_breadcrumb steps=s current=1 %}",
        {"s": ["Ok", "", None, {"label": "Dict"}]},
    )
    assert "Ok" in html
    assert "Dict" in html


# -- velora_new_progress_bar (10.12) --------------------------------------


def test_new_progress_bar_renders_counter_and_bar():
    html = render(
        "{% load velora_navigation %}{% velora_new_progress_bar current=3 total=10 label='Upload' %}"
    )
    assert "velora-progress-xy" in html
    assert "Upload" in html
    assert ">3<" in html
    assert ">10<" in html
    assert "di" in html
    assert 'role="progressbar"' in html
    assert 'aria-valuenow="3"' in html
    assert 'aria-valuemax="10"' in html
    assert "width: 30.00%;" in html


def test_new_progress_bar_total_zero_no_bar():
    html = render(
        "{% load velora_navigation %}{% velora_new_progress_bar current=0 total=0 %}"
    )
    assert "velora-progress-xy" in html
    assert "velora-progress-xy__track" not in html
    assert 'role="progressbar"' not in html


def test_new_progress_bar_clamps_current_to_total():
    html = render(
        "{% load velora_navigation %}{% velora_new_progress_bar current=20 total=10 %}"
    )
    assert ">10<" in html
    # current dovrebbe essere clampato a 10
    assert 'aria-valuenow="10"' in html


def test_new_progress_bar_negative_inputs():
    html = render(
        "{% load velora_navigation %}{% velora_new_progress_bar current=-5 total=-3 %}"
    )
    # entrambi normalizzati a 0; senza barra
    assert ">0<" in html
    assert "velora-progress-xy__track" not in html
