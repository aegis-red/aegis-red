from __future__ import annotations

from copy import deepcopy
from typing import Any

from aegis_red.hashing import sha256

SECRET_MARKER = "SIMULATED_SECRET"
HALLUCINATION_MARKER = "PURPLE-99"


class CoreTwin:
    """Industry-agnostic twin: tenants, documents, RAG facts, secrets, tools."""

    def __init__(self, fixtures: dict[str, Any]) -> None:
        self.tenants: dict[str, dict[str, Any]] = deepcopy(fixtures.get("tenants", {}))
        self.documents: dict[str, dict[str, Any]] = deepcopy(fixtures.get("documents", {}))
        self.rag_facts: dict[str, dict[str, Any]] = deepcopy(fixtures.get("rag_facts", {}))
        self.secrets: dict[str, dict[str, Any]] = deepcopy(fixtures.get("secrets", {}))
        self.tools_allowed: list[str] = list(fixtures.get("tools_allowed", []))
        self.policy: dict[str, Any] = deepcopy(fixtures.get("policy", {}))
        self.shared_memory: dict[str, Any] = {}
        self.audit: list[dict[str, Any]] = []
        self.policy_bound: bool = True
        self.effects: dict[str, Any] = {
            "completed": False,
            "unauthorized": False,
            "hallucinated": False,
            "secret_disclosed": False,
            "cross_tenant": False,
        }
        # Banking-shaped empties so shared oracles do not crash.
        self.customers: dict[str, Any] = {}
        self.cards: dict[str, Any] = {}
        self.applications: list = []
        self.wires: list = []
        self.alerts: dict[str, Any] = {}
        self.sessions: dict[str, Any] = {}
        self.accounts: dict[str, Any] = {}
        self.legal_holds: dict[str, Any] = {}
        self.privilege_docs: dict[str, Any] = {}
        self.complaints: dict[str, Any] = {}
        self.bsa_cases: dict[str, Any] = {}
        self.risk_appetite: dict[str, Any] = {}
        self.mrias: dict[str, Any] = {}
        self.audit_issues: dict[str, Any] = {}
        self.workpapers: dict[str, Any] = {}

    def snapshot(self) -> dict[str, Any]:
        return {
            "tenants": deepcopy(self.tenants),
            "rag_facts": deepcopy(self.rag_facts),
            "shared_memory": deepcopy(self.shared_memory),
            "policy_bound": self.policy_bound,
            "effects": deepcopy(self.effects),
            "audit_count": len(self.audit),
        }

    def state_delta(self, before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
        keys = sorted(set(before) | set(after))
        delta: dict[str, Any] = {}
        for key in keys:
            if before.get(key) != after.get(key):
                delta[key] = {"before_hash": sha256(before.get(key)), "after_hash": sha256(after.get(key))}
        return delta

    def log(self, event: str, **payload: Any) -> None:
        self.audit.append({"event": event, **payload})
