"""Smoke checks for template validation and placeholder release blocking."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import package_plugins

ROOT = Path(__file__).resolve().parents[2]
PACKAGER = ROOT / "scripts" / "package_plugins.py"


class TemplatePackagingTests(unittest.TestCase):
    def test_mit_license_allows_plugin_owner_copyright(self) -> None:
        license_text = package_plugins.MIT_LICENSE_TEXT.replace(
            "Copyright (c) 2026 Pupujiang", "Copyright (c) 2026 wtwang1998"
        )
        package_plugins._require_mit_license_text(
            license_text.encode("utf-8"), subject="plugin LICENSE"
        )

    def test_release_mit_license_rejects_the_template_copyright_for_other_authors(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError, "replace the template copyright holder"
        ):
            package_plugins._validate_plugin_license_text(
                package_plugins.MIT_LICENSE_TEXT.encode("utf-8"),
                license_expression="MIT",
                author="community-author",
            )

    def test_template_placeholders_are_rejected_for_release(self) -> None:
        manifest = json.loads((ROOT / "plugin" / "manifest.json").read_text())
        manifest["id"] = "org.example.plugin-template"
        with tempfile.TemporaryDirectory() as temporary_dir:
            manifest_path = Path(temporary_dir) / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "replace the template plugin id"):
                package_plugins._load_manifest(manifest_path, allow_template=False)
        with self.assertRaisesRegex(ValueError, "template placeholder"):
            package_plugins._reject_template_placeholders(
                {"personas.json": b"Replace with a persona"}
            )

    def test_registry_compatible_spdx_expressions_are_accepted(self) -> None:
        for expression in (
            "MIT",
            "Apache-2.0 OR MIT",
            "GPL-2.0-or-later WITH Classpath-exception-2.0",
            "(Apache-2.0 AND MIT) OR LicenseRef-Company-Data",
            # Mirror the Registry parser's accepted syntax exactly.
            "MIT WITH Classpath-exception-2.0",
        ):
            with self.subTest(expression=expression):
                package_plugins._validate_declared_license(expression)

    def test_spdx_database_is_pinned_to_registry_policy_version(self) -> None:
        policy = json.loads(package_plugins.SPDX_DATA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(policy["license_list_version"], "3.29.0")

    def test_release_manifest_accepts_non_mit_and_rejects_unknown_license(self) -> None:
        manifest = json.loads((ROOT / "plugin" / "manifest.json").read_text())
        manifest.update(
            {
                "id": "org.community.sample-plugin",
                "name": "Sample Plugin",
                "version": "1.0.0",
                "description": "A sample data-only plugin.",
                "author": "community-author",
                "license": "Apache-2.0 OR MIT",
            }
        )
        with tempfile.TemporaryDirectory() as temporary_dir:
            manifest_path = Path(temporary_dir) / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            loaded = package_plugins._load_manifest(manifest_path, allow_template=False)
            self.assertEqual(loaded["license"], "Apache-2.0 OR MIT")
            manifest["license"] = "Unknown-License-1.0"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown SPDX license"):
                package_plugins._load_manifest(manifest_path, allow_template=False)

    def test_invalid_or_unresolved_spdx_expressions_are_rejected(self) -> None:
        for expression in (
            "CHOOSE_LICENSE",
            "NONE",
            "NOASSERTION",
            "Unknown-License-1.0",
            "MIT OR",
            "Apache 2.0",
            "(MIT",
        ):
            with (
                self.subTest(expression=expression),
                self.assertRaises(ValueError),
            ):
                package_plugins._validate_declared_license(expression)

    def test_package_accepts_non_mit_spdx_with_declared_license_text(self) -> None:
        manifest = {
            "license": "Apache-2.0",
            "author": "community-author",
            "resources": {},
        }
        files = {
            "manifest.json": b"{}",
            "README.md": b"A sample plugin.",
            "LICENSE": (
                b"SPDX-License-Identifier: Apache-2.0\n"
                b"Apache License\nVersion 2.0, January 2004\n"
                + b"Terms and conditions for use, reproduction, and distribution.\n"
                * 4
            ),
            "personas.json": b"{}",
        }
        with tempfile.TemporaryDirectory() as temporary_dir:
            source = Path(temporary_dir)
            for name, content in files.items():
                (source / name).write_bytes(content)
            packed = package_plugins._package_files(
                source, manifest, allow_template=False
            )
        self.assertEqual(packed["LICENSE"], files["LICENSE"])

    def test_package_rejects_missing_placeholder_or_mismatched_license_text(
        self,
    ) -> None:
        manifest = {
            "license": "Apache-2.0",
            "author": "community-author",
            "resources": {},
        }
        invalid_license_texts = (
            b"",
            b"Choose the plugin license and put its complete text here.",
            b"SPDX-License-Identifier: MIT\n" + b"x" * 200,
            b"SPDX-License-Identifier: Apache-2.0\n"
            + b"Copyright (c) 2026 Pupujiang\n"
            + b"x" * 200,
        )
        for license_text in invalid_license_texts:
            with (
                self.subTest(license_text=license_text[:40]),
                tempfile.TemporaryDirectory() as temporary_dir,
            ):
                source = Path(temporary_dir)
                (source / "manifest.json").write_text("{}", encoding="utf-8")
                (source / "LICENSE").write_bytes(license_text)
                with self.assertRaises(ValueError):
                    package_plugins._package_files(
                        source, manifest, allow_template=False
                    )

    def test_repository_source_passes_check(self) -> None:
        check = subprocess.run(
            [sys.executable, str(PACKAGER), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(check.returncode, 0, check.stderr)


if __name__ == "__main__":
    unittest.main()
