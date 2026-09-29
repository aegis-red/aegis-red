from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in here.parents:
        if (candidate / "aegis.yaml").exists():
            return candidate
        if (candidate / "catalog" / "domains" / "banking" / "taxonomy.yaml").exists():
            return candidate
        if (candidate / "catalog" / "taxonomy.yaml").exists():
            return candidate
    return Path.cwd()


def catalog_dir() -> Path:
    return repo_root() / "catalog"


def banking_dir() -> Path:
    return catalog_dir() / "domains" / "banking"


def core_dir() -> Path:
    return catalog_dir() / "core"


def aegis_config() -> dict[str, Any]:
    path = repo_root() / "aegis.yaml"
    if not path.exists():
        return {
            "packs": [
                {"id": "core", "path": "catalog/core"},
                {"id": "banking", "path": "catalog/domains/banking"},
            ]
        }
    with path.open() as fh:
        return yaml.safe_load(fh) or {}


def pack_roots() -> list[Path]:
    roots: list[Path] = []
    for pack in aegis_config().get("packs", []):
        raw = pack.get("path", "")
        path = repo_root() / raw if raw else None
        if path and path.exists():
            roots.append(path)
    if not roots:
        if core_dir().exists():
            roots.append(core_dir())
        if banking_dir().exists():
            roots.append(banking_dir())
        elif (catalog_dir() / "taxonomy.yaml").exists():
            roots.append(catalog_dir())
    return roots


def evidence_dir() -> Path:
    path = repo_root() / "data" / "evidence"
    path.mkdir(parents=True, exist_ok=True)
    return path


def static_dir() -> Path:
    return Path(__file__).resolve().parent / "static"
