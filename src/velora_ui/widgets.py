"""Widget Django custom di Velora UI.

Questi widget sono pensati per essere usati con `forms.Form` / `ModelForm`
del progetto host quando la view sceglie il rendering "Django nativo"
invece dei nostri tag {% velora_form_row %}. Il template di ogni widget
riusa gli stessi partial dei tag, cosi` lo stile resta consistente.

In v0.1 (M3) esponiamo:

  - ``OnOffWidget``: <input type=checkbox> stilizzato come switch on/off,
    coerente con il template form_row/onoff.html.

Altri widget (DatePicker, MultiSelect, ecc.) arriveranno con M3 esteso
in v0.2 / v0.3 (vedi piano).
"""

from __future__ import annotations

from typing import Any

from django import forms


class OnOffWidget(forms.CheckboxInput):
    """Checkbox renderizzato come switch on/off.

    Si comporta come ``forms.CheckboxInput`` standard a livello di valori
    (post: ``value_on`` se selezionato, assente altrimenti) ma usa un
    template che applica le classi Velora `velora-form-row__onoff*`.

    Esempio d'uso:

        class MyForm(forms.Form):
            notifications = forms.BooleanField(
                required=False,
                widget=OnOffWidget(),
            )
    """

    template_name = "velora_ui/widgets/onoff.html"

    def __init__(
        self,
        attrs: dict[str, Any] | None = None,
        check_test: Any = None,
        value_on: str = "1",
    ) -> None:
        super().__init__(attrs=attrs, check_test=check_test)
        self.value_on = value_on

    def get_context(
        self, name: str, value: Any, attrs: dict[str, Any] | None
    ) -> dict[str, Any]:
        context = super().get_context(name, value, attrs)
        context["widget"]["value_on"] = self.value_on
        return context
