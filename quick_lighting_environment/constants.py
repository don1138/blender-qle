# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared Quick Lighting Environment identifiers."""

from pathlib import Path
import tomllib


def version_label():
    manifest_path = Path(__file__).with_name("blender_manifest.toml")
    with manifest_path.open("rb") as manifest_file:
        return tomllib.load(manifest_file)["version"]
