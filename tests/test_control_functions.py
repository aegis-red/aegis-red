from aegis_red.catalog import Catalog
from aegis_red.control_function_seeds import build_pack
from aegis_red.evidence import EvidenceLake
from aegis_red.runner import CampaignRunner


REQUIRED_CONTROL_IDS = {
    "DOM-LEGAL-001",
    "DOM-LEGAL-002",
    "DOM-COMP-002",
    "DOM-RISK-003",
    "DOM-MKT-002",
    "REG-FW-003",
    "DOM-IA-002",
    "SWARM-LEGAL-001",
}


def test_control_function_pack_is_96():
    pack = build_pack()
    assert len(pack) == 96
    families = {s["family"] for s in pack}
    assert families >= {
        "legal",
        "compliance",
        "risk",
        "marketing",
        "regulatory_framework",
        "internal_audit",
    }


def test_catalog_includes_control_function_domains():
    cat = Catalog()
    missing = REQUIRED_CONTROL_IDS - set(cat.seeds)
    assert not missing, missing
    assert cat.seeds["DOM-LEGAL-002"].family == "legal"
    assert cat.seeds["REG-FW-003"].pillar.value == "regulator"
    assert cat.persona("good.internal_auditor").class_.value == "good"
    assert len(cat.seeds) >= 332


def test_control_functions_hold_on_secure(tmp_path):
    runner = CampaignRunner(Catalog(), EvidenceLake(tmp_path))
    summary = runner.run("control_functions")
    assert summary.coverage_complete
    assert summary.go_no_go == "go"
    assert summary.outcomes.get("hold") == summary.bundle_count


def test_control_functions_leaky_breaches_named(tmp_path):
    runner = CampaignRunner(Catalog(), EvidenceLake(tmp_path))
    summary = runner.run("control_functions", sut_mode="leaky")
    bundles = {b["seed_id"]: b for b in runner.lake.load_all_bundles(summary.engagement_id)}
    assert bundles["DOM-LEGAL-002"]["outcome"] == "breach"
    assert bundles["DOM-COMP-002"]["outcome"] == "breach"
    assert bundles["DOM-IA-002"]["outcome"] == "breach"
    assert bundles["DOM-LEGAL-001"]["outcome"] == "hold"
