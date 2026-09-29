"""Discover pack YAML and installed plugins. Core stays small; packs grow coverage."""

from __future__ import annotations

from importlib.metadata import entry_points
from pathlib import Path
from typing import Any, Callable

import yaml

from aegis_red.paths import pack_roots


SUT_GROUP = "aegis_red.sut"
ORACLE_GROUP = "aegis_red.oracles"


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open() as fh:
        data = yaml.safe_load(fh) or {}
    return data if isinstance(data, dict) else {}


def load_pack_intercepts() -> dict[str, dict[str, Any]]:
    """Merge extensions/policy_intercepts.yaml from every enabled pack."""
    merged: dict[str, dict[str, Any]] = {}
    for pack in pack_roots():
        path = pack / "extensions" / "policy_intercepts.yaml"
        if not path.exists():
            continue
        for row in _read_yaml(path).get("intercepts") or []:
            if not isinstance(row, dict) or not row.get("id"):
                continue
            merged[str(row["id"])] = {
                "label": row.get("label") or row["id"],
                "claim": row.get("claim") or "",
                "expand": list(row.get("expand") or []),
                "effect": row.get("effect") or "",
            }
    return merged


def iter_entry_points(group: str) -> list[tuple[str, Callable[..., Any]]]:
    found: list[tuple[str, Callable[..., Any]]] = []
    try:
        eps = entry_points()
        selected = eps.select(group=group) if hasattr(eps, "select") else eps.get(group, [])
    except Exception:
        return found
    for ep in selected:
        try:
            found.append((ep.name, ep.load()))
        except Exception:
            continue
    return found


def list_extensions() -> dict[str, Any]:
    return {
        "packs": [str(path) for path in pack_roots()],
        "pack_intercepts": sorted(load_pack_intercepts()),
        "sut_plugins": [name for name, _ in iter_entry_points(SUT_GROUP)],
        "oracle_plugins": [name for name, _ in iter_entry_points(ORACLE_GROUP)],
    }
