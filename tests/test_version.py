"""Guards against version drift between the manifest and pyproject.toml."""

import json
import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]


def test_manifest_version_matches_pyproject() -> None:
    manifest = json.loads((_REPO_ROOT / "custom_components" / "mtec" / "manifest.json").read_text())
    with (_REPO_ROOT / "pyproject.toml").open("rb") as fh:
        pyproject = tomllib.load(fh)
    assert manifest["version"] == pyproject["project"]["version"]
