"""Test {% velora_assets %} con static() vs prefisso GitHub Release."""

from __future__ import annotations

import re

from django.core.exceptions import ImproperlyConfigured
from django.template import Context, Template
from django.test import TestCase, override_settings

from velora_ui import __version__


def _render_assets() -> str:
    return Template("{% load velora_assets %}{% velora_assets %}").render(Context())


class VeloraAssetsTagTests(TestCase):
    def test_default_uses_static_paths(self) -> None:
        out = _render_assets()
        self.assertIn("velora_ui/css/velora.css", out)
        self.assertIn("velora_ui/js/velora.js", out)

    @override_settings(VELORA_ASSETS_BASE_URL="")
    def test_empty_string_uses_static(self) -> None:
        out = _render_assets()
        self.assertIn("velora.css", out)
        self.assertIn("velora.js", out)

    @override_settings(
        VELORA_ASSETS_BASE_URL=f"https://github.com/owner/Velora/releases/download/v{__version__}/"
    )
    def test_release_base_emits_absolute_github_urls_full_js(self) -> None:
        out = _render_assets()
        ver = re.escape(__version__)
        self.assertRegex(
            out,
            rf'https://github\.com/owner/Velora/releases/download/v{ver}/velora-{ver}\.min\.css',
        )
        self.assertRegex(
            out,
            rf'https://github\.com/owner/Velora/releases/download/v{ver}/velora-{ver}\.full\.min\.js',
        )

    @override_settings(
        VELORA_ASSETS_BASE_URL=f"https://github.com/owner/Velora/releases/download/v{__version__}",
        VELORA_ASSETS_JS_FULL=False,
    )
    def test_release_base_core_js(self) -> None:
        out = _render_assets()
        self.assertIn(f"velora-{__version__}.min.js", out)
        self.assertNotIn(f"velora-{__version__}.full.min.js", out)

    @override_settings(VELORA_ASSETS_BASE_URL="http://github.com/o/r/releases/download/v1.0.0/")
    def test_rejects_non_https(self) -> None:
        with self.assertRaises(ImproperlyConfigured):
            _render_assets()

    @override_settings(
        VELORA_ASSETS_BASE_URL="https://cdn.example.com/releases/download/v1.0.0/"
    )
    def test_rejects_non_github_host(self) -> None:
        with self.assertRaises(ImproperlyConfigured):
            _render_assets()

    @override_settings(VELORA_ASSETS_BASE_URL="https://github.com/o/r/blob/main/dist/")
    def test_rejects_path_without_releases_download(self) -> None:
        with self.assertRaises(ImproperlyConfigured):
            _render_assets()
