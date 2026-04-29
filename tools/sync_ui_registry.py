#!/usr/bin/env python3
"""Genera partial Django (e frammenti statici documentati) da ui_registry/.

Uso:
  python tools/sync_ui_registry.py --check   # CI: fallisce se c'è drift
  python tools/sync_ui_registry.py --write   # aggiorna i file generati nel working tree
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Segnaposto nei file part (HTML neutro): |||nome||| → {{ nome }} (Django) o valore (static)
PLACEHOLDER_RE = re.compile(r"\|\|\|(\w+)\|\|\|")


def part_to_django(content: str) -> str:
    return PLACEHOLDER_RE.sub(lambda m: "{{ " + m.group(1) + " }}", content)


def part_to_static(content: str, subs: dict[str, str]) -> str:
    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        if key in subs:
            return subs[key]
        raise KeyError(f"Chiave mancante nelle sostituzioni statiche: {key}")

    return PLACEHOLDER_RE.sub(repl, content)


def load_segment(repo_root: Path, seg: dict) -> str:
    if "literal_file" in seg:
        path = repo_root / seg["literal_file"]
        return path.read_text(encoding="utf-8")
    if "part" in seg:
        path = repo_root / seg["part"]
        return part_to_django(path.read_text(encoding="utf-8"))
    if "django" in seg:
        return seg["django"]
    raise ValueError(f"Segmento registry sconosciuto: {seg!r}")


def build_django(repo_root: Path, segments: list[dict]) -> str:
    return "".join(load_segment(repo_root, s) for s in segments)


def build_static_fragment(repo_root: Path, segments: list[dict], subs: dict[str, str]) -> str:
    chunks: list[str] = []
    for seg in segments:
        if "part" not in seg:
            continue
        path = repo_root / seg["part"]
        chunks.append(part_to_static(path.read_text(encoding="utf-8"), subs))
    return "".join(chunks).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--check", action="store_true")
    grp.add_argument("--write", action="store_true")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    reg_path = repo_root / "ui_registry" / "registry.json"
    data = json.loads(reg_path.read_text(encoding="utf-8"))
    failures: list[tuple[Path, str]] = []

    for build in data["builds"]:
        out_path = repo_root / build["output"]
        text = build_django(repo_root, build["segments"])
        if args.check:
            existing = out_path.read_text(encoding="utf-8")
            if existing != text:
                failures.append((out_path, "drift partial Django rispetto a ui_registry"))
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(text, encoding="utf-8", newline="\n")

        static_cfg = build.get("static_example")
        if static_cfg:
            static_out = repo_root / static_cfg["output"]
            subs = static_cfg["substitutions"]
            try:
                static_text = build_static_fragment(repo_root, build["segments"], subs)
            except KeyError as e:
                failures.append((static_out, str(e)))
                continue
            if args.check:
                if not static_out.exists():
                    failures.append((static_out, "file frammento statico mancante"))
                else:
                    ex = static_out.read_text(encoding="utf-8")
                    if ex != static_text:
                        failures.append((static_out, "drift frammento statico"))
            else:
                static_out.parent.mkdir(parents=True, exist_ok=True)
                static_out.write_text(static_text, encoding="utf-8", newline="\n")

    if failures:
        for path, reason in failures:
            print(f"{reason}: {path.relative_to(repo_root)}", file=sys.stderr)
        sys.exit(1)
    print("ui_registry: OK", file=sys.stderr)


if __name__ == "__main__":
    main()
