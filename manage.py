#!/usr/bin/env python
"""Entry point standard di Django per comandi amministrativi (runserver, migrate, ecc.)."""

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "velora_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossibile importare Django. Assicurati che sia installato e disponibile "
            "nel PYTHONPATH, e che l'ambiente virtuale sia attivo (oppure stai eseguendo "
            "dentro il container `web`)."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
