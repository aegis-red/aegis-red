from aegis_red.catalog import Catalog
from aegis_red.evidence import EvidenceLake
from aegis_red.governor import Governor, GovernorDenied
from aegis_red.models import Campaign, Environment, Outcome
from aegis_red.runner import CampaignRunner


def test_card_cert_holds_on_secure_twin(tmp_path):
    runner = CampaignRunner(Catalog(), EvidenceLake(tmp_path))
    summary = runner.run("preprod_card_cert")
    assert summary.coverage_complete
    assert summary.go_no_go == "go"
    assert summary.outcomes.get("hold") == summary.bundle_count
    assert "breach" not in summary.outcomes


def test_leaky_mesh_produces_breach_evidence(tmp_path):
    runner = CampaignRunner(Catalog(), EvidenceLake(tmp_path))
    summary = runner.run("demo_leaky_mesh")
    assert summary.go_no_go == "no-go"
    assert summary.outcomes.get("breach", 0) >= 1
    bundles = runner.lake.load_all_bundles(summary.engagement_id)
    phantom = next(b for b in bundles if b["seed_id"] == "DOM-OFFER-002")
    assert phantom["outcome"] == "breach"
    assert phantom["bundle_hash"]
    assert phantom["lineage"]["seed_id"] == "DOM-OFFER-002"


def test_swarm_campaign_writes_mesh_evidence(tmp_path):
    runner = CampaignRunner(Catalog(), EvidenceLake(tmp_path))
    summary = runner.run("uc_swarm")
    assert summary.coverage_complete
    assert summary.go_no_go == "go"
    bundles = runner.lake.load_all_bundles(summary.engagement_id)
    swarm = next(b for b in bundles if b["seed_id"] == "SWARM-OFFER-ACT-001")
    assert swarm["swarm"]["graph"]["edges"]
    assert swarm["outcome"] == Outcome.hold.value
    assert (tmp_path / summary.engagement_id / "swarm_graph.json").exists()


def test_wire_cert_dual_control(tmp_path):
    runner = CampaignRunner(Catalog(), EvidenceLake(tmp_path))
    summary = runner.run("preprod_wire_cert")
    assert summary.go_no_go == "go"
    cells = runner.lake.load_coverage(summary.engagement_id)
    assert {c["seed_id"] for c in cells} >= {"DOM-WIRE-004", "DOM-FRAUD-001", "DOM-TAIL-001"}


def test_governor_blocks_leaky_in_prod():
    cat = Catalog()
    campaign = cat.campaigns["demo_leaky_mesh"].model_copy(update={"env": Environment.prod})
    gov = Governor()
    try:
        gov.issue("e", campaign, cat.seeds["DOM-OFFER-002"])
        raised = False
    except GovernorDenied:
        raised = True
    assert raised


def test_every_selected_seed_has_a_bundle(tmp_path):
    cat = Catalog()
    runner = CampaignRunner(cat, EvidenceLake(tmp_path))
    summary = runner.run("preprod_card_cert")
    cells = runner.lake.load_coverage(summary.engagement_id)
    selected = set(cat.campaigns["preprod_card_cert"].select.seed_ids)
    assert {c["seed_id"] for c in cells} == selected
    assert all(c["bundle_hash"] for c in cells)
