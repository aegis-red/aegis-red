"""Live demo SUT: a real HTTP agent the harness can hit. Twin-backed, not an exploit sandbox."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from aegis_red.models import Persona, Seed, Turn
from aegis_red.sut_adapter import TwinAdapter
from aegis_red.twin_state import export_state

app = FastAPI(title="Aegis Red demo SUT", version="0.1.0")


class TurnRequest(BaseModel):
    seed: dict[str, Any]
    persona: dict[str, Any]
    utterance: str
    fixtures: dict[str, Any] = Field(default_factory=dict)
    mode: str = "secure"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "role": "demo-sut", "kind": "twin-backed"}


@app.post("/v1/assurance/turn")
def handle_turn(req: TurnRequest) -> dict[str, Any]:
    seed = Seed.model_validate(req.seed)
    persona = Persona.model_validate(req.persona)
    adapter = TwinAdapter(req.fixtures, seed, req.mode)
    turn: Turn = adapter.handle(seed, persona, req.utterance)
    return {
        "turn": turn.model_dump(mode="json"),
        "twins_state": export_state(adapter.twins),
        "policy_bound": bool(getattr(adapter.twins, "policy_bound", True)),
        "sut": "aegis-red-demo",
    }
