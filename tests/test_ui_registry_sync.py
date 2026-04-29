"""Gate CI: partial Django per componenti registrati = output di ui_registry."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_ui_registry_sync_check() -> None:
    script = ROOT / "tools" / "sync_ui_registry.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
