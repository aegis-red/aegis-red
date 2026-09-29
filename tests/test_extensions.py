from aegis_red.catalog import Catalog
from aegis_red.evidence import EvidenceLake
from aegis_red.extensions import list_extensions, load_pack_intercepts
from aegis_red.policy_intercept import all_intercepts
from aegis_red.runner import CampaignRunner
from aegis_red.sut_adapter import TwinAdapter, build_adapter


def test_seed_store_pack_is_loaded():
    cat = Catalog()
    assert "CONTRIB-TOOL-001" in cat.seeds
    assert "CONTRIB-TOOL-002" in cat.seeds
    assert "CONTRIB-POLICY-001" in cat.seeds
    assert "seed_store" in cat.campaigns


def test_pack_policy_intercepts_merge_into_form():
    ids = set(all_intercepts())
    assert "expand_read_tools" in ids
    assert "expand_write_tools" in ids
    assert "expand_read_tools" in load_pack_intercepts()
    info = list_extensions()
    assert any("seed_store" in path for path in info["packs"])


def test_twin_adapter_is_the_default(tmp_path):
    cat = Catalog()
    seed = cat.seed("CONTRIB-TOOL-001")
    adapter = build_adapter(cat.fixtures, seed, "secure")
    assert isinstance(adapter, TwinAdapter)
    runner = CampaignRunner(cat, EvidenceLake(tmp_path))
    summary = runner.run("seed_store")
    assert summary.coverage_complete
    assert summary.outcomes.get("hold") == summary.bundle_count
    assert summary.go_no_go == "go"
