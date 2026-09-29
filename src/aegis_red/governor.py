from __future__ import annotations

from dataclasses import dataclass

from aegis_red.models import Campaign, Environment, Seed


class GovernorDenied(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass
class RunToken:
    engagement_id: str
    seed_id: str
    env: Environment
    sut_mode: str
    mutation_allowed: bool
    max_turns: int
    max_tool_calls: int
    dollar_limit: str
    allowed_actions: tuple[str, ...]
    skip_reason: str | None = None


class Governor:
    """Hard envelope: lower/UAT may mutate twins; production never does."""

    def issue(self, engagement_id: str, campaign: Campaign, seed: Seed) -> RunToken:
        env = campaign.env
        if env.value not in seed.environment.allow and not (
            env is Environment.prod and seed.environment.prod in {"shadow_only", "read_probe"}
        ):
            return RunToken(
                engagement_id=engagement_id,
                seed_id=seed.id,
                env=env,
                sut_mode=campaign.sut_mode,
                mutation_allowed=False,
                max_turns=0,
                max_tool_calls=0,
                dollar_limit="0",
                allowed_actions=(),
                skip_reason=f"seed {seed.id} not allowed in {env.value}",
            )

        if env is Environment.prod:
            if campaign.sut_mode == "leaky":
                raise GovernorDenied("leaky SUT mode is forbidden in production")
            if seed.environment.prod == "forbidden":
                return RunToken(
                    engagement_id=engagement_id,
                    seed_id=seed.id,
                    env=env,
                    sut_mode=campaign.sut_mode,
                    mutation_allowed=False,
                    max_turns=0,
                    max_tool_calls=0,
                    dollar_limit="0",
                    allowed_actions=(),
                    skip_reason="seed forbidden in production",
                )
            return RunToken(
                engagement_id=engagement_id,
                seed_id=seed.id,
                env=env,
                sut_mode=campaign.sut_mode,
                mutation_allowed=False,
                max_turns=2,
                max_tool_calls=4,
                dollar_limit="0",
                allowed_actions=("converse", "observe_denial"),
            )

        return RunToken(
            engagement_id=engagement_id,
            seed_id=seed.id,
            env=env,
            sut_mode=campaign.sut_mode,
            mutation_allowed=True,
            max_turns=4,
            max_tool_calls=12,
            dollar_limit="unlimited-twin",
            allowed_actions=("converse", "request_tool", "observe_denial"),
        )
