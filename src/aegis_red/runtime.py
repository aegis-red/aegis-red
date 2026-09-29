"""Process-level overrides so the portal and CLI can pick a live SUT without editing YAML."""

from __future__ import annotations

import os
from typing import Any

from aegis_red.paths import aegis_config

_override: dict[str, Any] = {}


def set_sut_override(values: dict[str, Any] | None) -> None:
    global _override
    _override = dict(values or {})


def sut_settings() -> dict[str, Any]:
    cfg = dict(aegis_config().get("sut") or {})
    cfg.update(_override)
    if os.environ.get("AEGIS_SUT_KIND"):
        cfg["kind"] = os.environ["AEGIS_SUT_KIND"]
    if os.environ.get("AEGIS_SUT_URL"):
        cfg["base_url"] = os.environ["AEGIS_SUT_URL"]
    cfg.setdefault("kind", "twin")
    cfg.setdefault("base_url", "http://127.0.0.1:8090")
    cfg.setdefault("auth_env", "AEGIS_SUT_TOKEN")
    return cfg
