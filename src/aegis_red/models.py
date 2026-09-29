from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Pillar(str, Enum):
    tech = "tech"
    domain = "domain"
    regulator = "regulator"


class PersonaClass(str, Enum):
    good = "good"
    bad = "bad"


class Topology(str, Enum):
    single = "single"
    swarm = "swarm"


class Outcome(str, Enum):
    hold = "hold"
    breach = "breach"
    over_block = "over_block"
    inconclusive = "inconclusive"
    skipped = "skipped"


class Environment(str, Enum):
    lower = "lower"
    uat = "uat"
    prod = "prod"


class Persona(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: str
    class_: PersonaClass = Field(alias="class")
    title: str
    goal: str
    channel: str
    description: str = ""
    role: str | None = None


class SeedTarget(BaseModel):
    model_config = ConfigDict(extra="allow")

    agent: str
    tools_in_scope: list[str] = Field(default_factory=list)


class SeedEnvironment(BaseModel):
    allow: list[str] = Field(default_factory=lambda: ["lower", "uat"])
    prod: str = "shadow_only"


class SeedFixtures(BaseModel):
    model_config = ConfigDict(extra="allow")

    customer: str | None = None
    card: str | None = None
    offer: str | None = None
    account: str | None = None
    employee_initiator: str | None = None
    employee_approver: str | None = None
    amount: str | None = None
    currency: str | None = None
    alert: str | None = None
    locked_session: str | None = None
    claimed_code: str | None = None
    channel_has_pan: bool | None = None
    required_factors_present: list[str] | None = None
    claimed_product: str | None = None
    claimed_plan: str | None = None


class PolicyIntercept(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = "none"
    claim: str = ""
    expand: list[str] = Field(default_factory=list)
    effect: str = ""


class Seed(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    journey: str
    step: str
    pillar: Pillar
    family: str
    control: str
    title: str
    intent: str
    persona: str
    target: SeedTarget
    environment: SeedEnvironment = Field(default_factory=SeedEnvironment)
    fixtures: SeedFixtures = Field(default_factory=SeedFixtures)
    utterance: str
    success_for_bank: list[str] = Field(default_factory=list)
    failure_for_bank: list[str] = Field(default_factory=list)
    severity: str = "high"
    reg_map: list[str] = Field(default_factory=list)
    topology: Topology = Topology.single
    pack: str = "banking"
    policy_intercept: PolicyIntercept | None = None

    @property
    def coverage_key(self) -> str:
        return f"{self.pillar.value}.{self.family}.{self.control}"


class CampaignSelect(BaseModel):
    seed_ids: list[str] = Field(default_factory=list)
    pillar: list[str] = Field(default_factory=list)
    family: list[str] = Field(default_factory=list)


class Campaign(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    title: str
    use_case: str
    env: Environment = Environment.lower
    sut_mode: str = "secure"
    topology: Topology = Topology.single
    select: CampaignSelect = Field(default_factory=CampaignSelect)
    personas: list[str] = Field(default_factory=list)
    gates: dict[str, Any] = Field(default_factory=dict)
    evidence: dict[str, Any] = Field(default_factory=dict)
    description: str = ""


class Journey(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    title: str
    description: str = ""
    steps: list[dict[str, Any]] = Field(default_factory=list)


class ToolDecision(str, Enum):
    allow = "allow"
    simulate = "simulate"
    deny = "deny"


class ToolCall(BaseModel):
    tool: str
    agent: str
    args: dict[str, Any] = Field(default_factory=dict)
    args_hash: str = ""
    decision: ToolDecision
    reason: str = ""
    result: dict[str, Any] = Field(default_factory=dict)


class Turn(BaseModel):
    index: int
    actor: str
    persona_id: str
    utterance: str
    sut_text: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    handoffs: list[dict[str, Any]] = Field(default_factory=list)


class OracleResult(BaseModel):
    name: str
    kind: str
    passed: bool
    fired: bool
    detail: str = ""
    evidence_ref: str = ""


class EvidenceBundle(BaseModel):
    coverage_key: str
    seed_id: str
    run_id: str
    engagement_id: str
    persona: str
    persona_class: PersonaClass
    topology: Topology
    journey: str
    step: str
    pillar: Pillar
    family: str
    outcome: Outcome
    severity: str
    oracles: list[OracleResult] = Field(default_factory=list)
    turns: list[Turn] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    snapshot_before: dict[str, Any] = Field(default_factory=dict)
    snapshot_after: dict[str, Any] = Field(default_factory=dict)
    state_delta: dict[str, Any] = Field(default_factory=dict)
    lineage: dict[str, Any] = Field(default_factory=dict)
    swarm: dict[str, Any] | None = None
    bundle_hash: str = ""
    prev_hash: str = ""
    created_at: datetime = Field(default_factory=utcnow)


class CoverageCell(BaseModel):
    coverage_key: str
    seed_id: str
    persona: str
    persona_class: str
    topology: str
    outcome: Outcome
    bundle_hash: str
    severity: str


class EngagementSummary(BaseModel):
    engagement_id: str
    campaign_id: str
    use_case: str
    env: Environment
    sut_mode: str
    topology: Topology
    started_at: datetime
    finished_at: datetime | None = None
    outcomes: dict[str, int] = Field(default_factory=dict)
    go_no_go: str = "pending"
    bundle_count: int = 0
    coverage_complete: bool = False
    chain_hash: str = ""
