from __future__ import annotations

from aegis_red.governor import RunToken
from aegis_red.models import Persona, Seed
from aegis_red.policy_intercept import apply_claim, from_seed


class RedActor:
    """Bounded planner: instantiate a seed utterance. No bank tools."""

    def __init__(self, persona: Persona) -> None:
        self.persona = persona

    def act(self, seed: Seed, token: RunToken) -> str:
        if token.skip_reason or token.max_turns <= 0:
            return ""
        prefix = f"[{self.persona.id} / {self.persona.class_.value}] "
        spoken = apply_claim(seed.utterance.strip(), from_seed(seed))
        return prefix + spoken
