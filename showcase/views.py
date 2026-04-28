from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from velora_ui import __version__ as velora_version


def index(request: HttpRequest) -> HttpResponse:
    """Pagina placeholder dello showcase: serve come smoke test del bootstrap.

    Verra` arricchita progressivamente nelle fasi successive del piano (M1..M6).
    Al momento si limita a confermare che il routing, i template e la app
    `velora_ui` sono caricati correttamente nel progetto host.
    """

    return render(
        request,
        "showcase/index.html",
        context={"velora_version": velora_version},
    )
