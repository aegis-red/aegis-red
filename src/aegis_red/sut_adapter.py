"""SUT adapters. Twin is built-in. Live HTTP demo is built-in. Other agents register via entry points."""

from __future__ import annotations

import os
from typing import Any, Protocol

import httpx

from aegis_red.core_sut import CoreMesh
from aegis_red.core_twin import CoreTwin
from aegis_red.extensions import SUT_GROUP, iter_entry_points
from aegis_red.models import Persona, Seed, Turn
from aegis_red.runtime import sut_settings
from aegis_red.sut import BankMesh
from aegis_red.twin_state import import_state
from aegis_red.twins import BankTwins


class SutAdapter(Protocol):
    twins: Any

    def handle(self, seed: Seed, persona: Persona, utterance: str) -> Turn: ...


class TwinAdapter:
    """In-process digital twin. Default for local and CI."""

    def __init__(self, fixtures: dict[str, Any], seed: Seed, mode: str) -> None:
        if seed.id.startswith("CORE-") or getattr(seed, "pack", None) == "core":
            self.twins = CoreTwin(fixtures)
            self._mesh = CoreMesh(self.twins, mode=mode)
        else:
            self.twins = BankTwins(fixtures)
            self._mesh = BankMesh(self.twins, mode=mode)

    def handle(self, seed: Seed, persona: Persona, utterance: str) -> Turn:
        return self._mesh.handle(seed, persona, utterance)


class HttpSutAdapter:
    """Live SUT over HTTP. Talks to `aegis-red demo-sut` or any compatible agent."""

    def __init__(
        self,
        fixtures: dict[str, Any],
        seed: Seed,
        mode: str,
        client: httpx.Client | None = None,
    ) -> None:
        inner = TwinAdapter(fixtures, seed, mode)
        self.twins = inner.twins
        self._fixtures = fixtures
        self._mode = mode
        cfg = sut_settings()
        self._base_url = str(cfg.get("base_url") or "http://127.0.0.1:8090").rstrip("/")
        auth_env = str(cfg.get("auth_env") or "AEGIS_SUT_TOKEN")
        self._token = os.environ.get(auth_env, "")
        self._client = client or httpx.Client(timeout=30.0)

    def handle(self, seed: Seed, persona: Persona, utterance: str) -> Turn:
        payload = {
            "seed": seed.model_dump(mode="json"),
            "persona": persona.model_dump(mode="json", by_alias=True),
            "utterance": utterance,
            "fixtures": self._fixtures,
            "mode": self._mode,
        }
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        try:
            response = self._client.post(
                f"{self._base_url}/v1/assurance/turn",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(
                "Live SUT is not reachable at "
                f"{self._base_url}. Start it with `aegis-red demo-sut` or "
                "`aegis-red try` (portal + live agent together)."
            ) from exc
        data = response.json()
        if "twins_state" in data:
            import_state(self.twins, data["twins_state"])
        return Turn.model_validate(data["turn"])


_BUILTIN: dict[str, Any] = {
    "twin": TwinAdapter,
    "http": HttpSutAdapter,
}


def build_adapter(fixtures: dict[str, Any], seed: Seed, mode: str) -> SutAdapter:
    kind = str(sut_settings().get("kind") or "twin")
    factory = _BUILTIN.get(kind)
    if factory is None:
        for name, loaded in iter_entry_points(SUT_GROUP):
            if name == kind:
                factory = loaded
                break
    if factory is None:
        raise RuntimeError(f"Unknown SUT kind {kind!r}. Use twin, http, or install a plugin.")
    return factory(fixtures, seed, mode)
