from aegis_red.catalog import Catalog
from aegis_red.evidence import EvidenceLake
from aegis_red.paths import aegis_config, pack_roots
from aegis_red.runner import CampaignRunner


def test_packs_include_core_and_banking():
    ids = [p["id"] for p in aegis_config()["packs"]]
    assert ids[:2] == ["core", "banking"]
    assert "seed_store" in ids
    names = [p.name for p in pack_roots()]
    assert "core" in names
    assert "banking" in names
    assert "seed_store" in names


def test_core_safety_campaign_holds(tmp_path):
    runner = CampaignRunner(Catalog(), EvidenceLake(tmp_path))
    summary = runner.run("core_safety")
    assert summary.coverage_complete
    assert summary.go_no_go == "go"
    assert summary.outcomes.get("hold") == summary.bundle_count
    assert all(sid.startswith("CORE-") for sid in runner.catalog.campaigns["core_safety"].select.seed_ids)


def test_core_safety_leaky_breaches_injection(tmp_path):
    runner = CampaignRunner(Catalog(), EvidenceLake(tmp_path))
    summary = runner.run("core_safety", sut_mode="leaky")
    bundles = {b["seed_id"]: b for b in runner.lake.load_all_bundles(summary.engagement_id)}
    assert bundles["CORE-INJECT-001"]["outcome"] == "breach"
    assert bundles["CORE-HALL-001"]["outcome"] == "breach"
    assert bundles["CORE-SAFE-002"]["outcome"] == "hold"
    assert bundles["CORE-HALL-002"]["outcome"] == "hold"
