from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from aegis_red.models import Campaign, Journey, Persona, Seed
from aegis_red.paths import catalog_dir, pack_roots


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open() as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def _load_seed_docs(path: Path) -> list[dict[str, Any]]:
    with path.open() as fh:
        data = yaml.safe_load(fh)
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "seeds" in data:
        return list(data["seeds"])
    if isinstance(data, dict) and "id" in data:
        return [data]
    raise ValueError(f"Unsupported seed YAML shape: {path}")


def _iter_yaml(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(folder.rglob("*.yaml"))


def _merge_dicts(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in incoming.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _merge_dicts(out[key], value)
        else:
            out[key] = value
    return out


class Catalog:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or catalog_dir()
        self.pack_roots = [root] if root and (root / "taxonomy.yaml").exists() else pack_roots()
        self.taxonomy: dict[str, Any] = {}
        self.personas: dict[str, Persona] = {}
        self.seeds: dict[str, Seed] = {}
        self.campaigns: dict[str, Campaign] = {}
        self.journeys: dict[str, Journey] = {}
        self.fixtures: dict[str, Any] = {}
        self.load()

    def reload(self) -> None:
        self.load()

    def load(self) -> None:
        self.taxonomy = {}
        self.fixtures = {}
        self.personas = {}
        self.seeds = {}
        self.campaigns = {}
        self.journeys = {}
        for pack in self.pack_roots:
            self._load_pack(pack)

    def _load_pack(self, pack: Path) -> None:
        tax = pack / "taxonomy.yaml"
        if tax.exists():
            self.taxonomy = _merge_dicts(self.taxonomy, _read_yaml(tax))
        fixtures_dir = pack / "fixtures"
        for fixture in _iter_yaml(fixtures_dir):
            self.fixtures = _merge_dicts(self.fixtures, _read_yaml(fixture))
        for path in _iter_yaml(pack / "personas"):
            persona = Persona.model_validate(_read_yaml(path))
            self.personas[persona.id] = persona
        for path in _iter_yaml(pack / "seeds"):
            for doc in _load_seed_docs(path):
                seed = Seed.model_validate(doc)
                if seed.id in self.seeds:
                    raise ValueError(f"Duplicate seed id {seed.id} in {path}")
                self.seeds[seed.id] = seed
        for path in _iter_yaml(pack / "campaigns"):
            campaign = Campaign.model_validate(_read_yaml(path))
            self.campaigns[campaign.id] = campaign
        for path in _iter_yaml(pack / "journeys"):
            journey = Journey.model_validate(_read_yaml(path))
            self.journeys[journey.id] = journey

    def persona(self, persona_id: str) -> Persona:
        if persona_id not in self.personas:
            raise KeyError(f"Unknown persona: {persona_id}")
        return self.personas[persona_id]

    def seed(self, seed_id: str) -> Seed:
        if seed_id not in self.seeds:
            raise KeyError(f"Unknown seed: {seed_id}")
        return self.seeds[seed_id]

    def campaign_seeds(self, campaign: Campaign) -> list[Seed]:
        selected = campaign.select.seed_ids
        if selected:
            return [self.seed(sid) for sid in selected]
        out: list[Seed] = []
        for seed in self.seeds.values():
            if campaign.select.pillar and seed.pillar.value not in campaign.select.pillar:
                continue
            if campaign.select.family and seed.family not in campaign.select.family:
                continue
            out.append(seed)
        return out

    def coverage_universe(self) -> list[str]:
        keys: list[str] = []
        for root_name in ("protect_organization", "protect_bank"):
            pillars = self.taxonomy.get(root_name, {}).get("pillars", {})
            for pillar_name, pillar in pillars.items():
                for family in pillar.get("families", {}):
                    keys.append(f"{pillar_name}.{family}")
        return keys
