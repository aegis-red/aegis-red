from aegis_red.catalog import Catalog
from aegis_red.evidence import EvidenceLake
from aegis_red.runner import CampaignRunner
from aegis_red.starter_seeds import build_pack


def test_pack_builder_is_204_unique():
    pack = build_pack()
    assert len(pack) == 204
    assert len({s["id"] for s in pack}) == 204


def test_starter_table_campaign_holds_on_secure(tmp_path):
    runner = CampaignRunner(Catalog(), EvidenceLake(tmp_path))
    summary = runner.run("starter_pack")
    assert summary.coverage_complete
    assert summary.go_no_go == "go"
    assert summary.outcomes.get("hold") == summary.bundle_count


def test_named_income_and_limit_oracles(tmp_path):
    runner = CampaignRunner(Catalog(), EvidenceLake(tmp_path))
    leaky = runner.run("starter_pack", sut_mode="leaky")
    bundles = {b["seed_id"]: b for b in runner.lake.load_all_bundles(leaky.engagement_id)}
    assert bundles["DOM-APPLY-003"]["outcome"] == "breach"
    assert bundles["DOM-LIM-002"]["outcome"] == "breach"
    assert bundles["DOM-OFFER-006"]["outcome"] == "breach"
    assert bundles["DOM-DEC-001"]["outcome"] == "hold"
