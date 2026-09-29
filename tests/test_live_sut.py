from urllib.parse import urlparse

from fastapi.testclient import TestClient

from aegis_red.catalog import Catalog
from aegis_red.demo_sut import app as demo_app
from aegis_red.evidence import EvidenceLake
from aegis_red.runner import CampaignRunner
from aegis_red.runtime import set_sut_override
from aegis_red.sut_adapter import HttpSutAdapter, TwinAdapter, build_adapter


class _PathClient:
    """Starlette TestClient wrapper so HttpSutAdapter can POST absolute URLs."""

    def __init__(self) -> None:
        self._inner = TestClient(demo_app)

    def _path(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.path if parsed.scheme else url

    def get(self, url: str, **kwargs):
        return self._inner.get(self._path(url), **kwargs)

    def post(self, url: str, **kwargs):
        return self._inner.post(self._path(url), **kwargs)


def test_demo_sut_health_and_turn():
    client = _PathClient()
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["role"] == "demo-sut"
    cat = Catalog()
    seed = cat.seed("CORE-SAFE-002")
    persona = cat.persona(seed.persona)
    res = client.post(
        "/v1/assurance/turn",
        json={
            "seed": seed.model_dump(mode="json"),
            "persona": persona.model_dump(mode="json", by_alias=True),
            "utterance": seed.utterance,
            "fixtures": cat.fixtures,
            "mode": "secure",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["turn"]["sut_text"]
    assert "twins_state" in body


def test_http_adapter_matches_twin_on_core_seed():
    cat = Catalog()
    seed = cat.seed("CORE-SAFE-002")
    persona = cat.persona(seed.persona)
    twin = TwinAdapter(cat.fixtures, seed, "secure")
    expected = twin.handle(seed, persona, seed.utterance)
    live = HttpSutAdapter(cat.fixtures, seed, "secure", client=_PathClient())
    got = live.handle(seed, persona, seed.utterance)
    assert got.sut_text == expected.sut_text
    assert [c.tool for c in got.tool_calls] == [c.tool for c in expected.tool_calls]


def test_seed_store_campaign_over_live_http(tmp_path, monkeypatch):
    demo = _PathClient()

    def factory(fixtures, seed, mode):
        return HttpSutAdapter(fixtures, seed, mode, client=demo)

    monkeypatch.setattr("aegis_red.runner.build_adapter", lambda fixtures, seed, mode: factory(fixtures, seed, mode))
    set_sut_override({"kind": "http", "base_url": "http://sut"})
    runner = CampaignRunner(Catalog(), EvidenceLake(tmp_path))
    summary = runner.run("seed_store")
    assert summary.coverage_complete
    assert summary.go_no_go == "go"
    assert summary.outcomes.get("hold") == summary.bundle_count
    bundle = runner.lake.load_all_bundles(summary.engagement_id)[0]
    assert bundle["lineage"]["sut_model"] == "aegis-red/http"


def test_default_adapter_is_still_twin():
    cat = Catalog()
    adapter = build_adapter(cat.fixtures, cat.seed("CONTRIB-TOOL-001"), "secure")
    assert isinstance(adapter, TwinAdapter)
