"""Copy twin internals across the HTTP hop so oracles still see live SUT effects."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def export_state(twin: Any) -> dict[str, Any]:
    return {key: deepcopy(value) for key, value in vars(twin).items() if not key.startswith("_")}


def import_state(twin: Any, state: dict[str, Any]) -> None:
    for key, value in state.items():
        if key.startswith("_") or not hasattr(twin, key):
            continue
        setattr(twin, key, deepcopy(value))
