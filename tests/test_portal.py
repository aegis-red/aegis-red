from fastapi.testclient import TestClient

from aegis_red.api import app
from aegis_red.portal import portal_payload


def test_portal_describes_problem_coverage_and_setup():
    payload = portal_payload()
    assert "secret" in payload["problem"].lower() or "policy" in payload["problem"].lower()
    ids = {row["id"] for row in payload["pillars"]}
    assert "injection" in ids
    assert "hallucination" in ids
    assert "privacy" in ids
    assert "policy" in ids
    assert "git clone" in payload["setup"]["mac"]["command"]
    assert "aegis-red" in payload["setup"]["mac"]["command"]
    assert "git clone" in payload["setup"]["windows"]["command"]
    assert "aegis-red" in payload["setup"]["windows"]["command"]
    kinds = {row["id"] for row in payload["contributions"]}
    assert {"seed", "intercept", "adapter"} <= kinds


def test_portal_api_and_home_page():
    client = TestClient(app)
    home = client.get("/")
    assert home.status_code == 200
    html = home.text
    assert "Try now" in html
    assert "Get started" in html
    assert "Contribute" in html
    assert "Mock test" in html
    portal = client.get("/api/portal")
    assert portal.status_code == 200
    body = portal.json()
    assert body["license"] == "Apache-2.0"
    assert body["seeds"] > 0
    assert body["sut"]["kind"] in {"twin", "http"}
    health = client.get("/api/health")
    assert health.status_code == 200
    assert "sut" in health.json()


def test_switching_to_live_sut_without_agent_fails_closed(monkeypatch):
    from aegis_red import api
    from aegis_red.runtime import sut_settings

    def status():
        kind = str(sut_settings().get("kind") or "twin")
        if kind == "http":
            return {
                "kind": "http",
                "base_url": "http://127.0.0.1:8090",
                "reachable": False,
                "label": "Live HTTP agent",
            }
        return {
            "kind": "twin",
            "base_url": "http://127.0.0.1:8090",
            "reachable": True,
            "label": "In-process twin (mock)",
        }

    monkeypatch.setattr(api, "_live_sut_status", status)
    client = TestClient(api.app)
    res = client.post("/api/sut", json={"kind": "http"})
    assert res.status_code == 503
    health = client.get("/api/health").json()
    assert health["sut"]["kind"] == "twin"
