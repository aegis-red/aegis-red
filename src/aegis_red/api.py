from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from aegis_red.catalog import Catalog
from aegis_red.evidence import EvidenceLake
from aegis_red.paths import static_dir
from aegis_red.portal import portal_payload
from aegis_red.runner import CampaignRunner
from aegis_red.policy_intercept import all_intercepts
from aegis_red.runtime import set_sut_override, sut_settings
from aegis_red.seed_author import form_options, save_seed, score_label

app = FastAPI(title="Aegis Red", version="0.1.0")
_catalog = Catalog()
_lake = EvidenceLake()
_runner = CampaignRunner(catalog=_catalog, lake=_lake)

static = static_dir()
if static.exists():
    app.mount("/assets", StaticFiles(directory=static), name="assets")


class RunRequest(BaseModel):
    campaign_id: str
    sut_mode: str | None = None
    env: str | None = None


class RunAllRequest(BaseModel):
    sut_mode: str | None = None
    env: str | None = None


class RunOneRequest(BaseModel):
    seed_id: str
    sut_mode: str | None = None
    env: str | None = None


class SeedFormRequest(BaseModel):
    area: str
    title: str
    what_they_say: str
    expectation: str = "should_refuse"
    policy_intercept: str = "none"


class SutRequest(BaseModel):
    kind: str = "twin"


def _transcript(bundle: dict[str, Any]) -> dict[str, Any]:
    sent: list[str] = []
    replies: list[str] = []
    for turn in bundle.get("turns") or []:
        if turn.get("utterance"):
            sent.append(turn["utterance"])
        if turn.get("sut_text"):
            replies.append(turn["sut_text"])
    tools = [
        {
            "who": call.get("agent") or "agent",
            "tool": call.get("tool") or "",
            "decision": call.get("decision") or "",
            "reason": call.get("reason") or "",
        }
        for call in bundle.get("tool_calls") or []
    ]
    checks = [
        {
            "name": oracle.get("name") or "",
            "passed": bool(oracle.get("passed")),
            "detail": oracle.get("detail") or "",
            "kind": oracle.get("kind") or "",
        }
        for oracle in bundle.get("oracles") or []
    ]
    return {
        "sent": "\n\n".join(sent),
        "agent_reply": "\n\n".join(replies),
        "tools": tools,
        "checks": checks,
    }


def _attach_transcripts(rows: list[dict[str, Any]], bundles: list[dict[str, Any]]) -> None:
    by_seed = {bundle.get("seed_id"): bundle for bundle in bundles}
    for row in rows:
        bundle = by_seed.get(row.get("seed_id"))
        if not bundle:
            continue
        row["run_id"] = bundle.get("run_id", "")
        row.update(_transcript(bundle))


def _capture_results(engagement_id: str) -> dict[str, Any]:
    coverage = _lake.load_coverage(engagement_id)
    rows: list[dict[str, Any]] = []
    passed = failed = other = 0
    for cell in coverage:
        seed = _catalog.seeds.get(cell["seed_id"])
        result, meaning = score_label(cell["outcome"])
        if result == "Pass":
            passed += 1
        elif result == "Fail":
            failed += 1
        else:
            other += 1
        rows.append(
            {
                "seed_id": cell["seed_id"],
                "title": seed.title if seed else cell["seed_id"],
                "area": cell.get("coverage_key", ""),
                "result": result,
                "meaning": meaning,
                "outcome": cell["outcome"],
                "expected": (seed.intent if seed else "") or meaning,
                "run_id": "",
                "sent": "",
                "agent_reply": "",
                "tools": [],
                "checks": [],
                "policy_intercept": getattr(getattr(seed, "policy_intercept", None), "id", None)
                if seed
                else None,
                "policy_intercept_label": all_intercepts().get(
                    getattr(getattr(seed, "policy_intercept", None), "id", "") or "",
                    {},
                ).get("label"),
            }
        )
    bundles = _lake.load_all_bundles(engagement_id)
    _attach_transcripts(rows, bundles)
    payload = {
        "engagement_id": engagement_id,
        "passed": passed,
        "failed": failed,
        "other": other,
        "total": len(rows),
        "rows": rows,
    }
    _lake.write_results(engagement_id, payload)
    return payload


def _run_and_score(campaign_id: str, sut_mode: str | None = None, env: str | None = None, seed_ids: list[str] | None = None) -> dict[str, Any]:
    summary = _runner.run(campaign_id, sut_mode=sut_mode, env=env, seed_ids=seed_ids)
    dumped = summary.model_dump(mode="json")
    dumped["results"] = _capture_results(summary.engagement_id)
    return dumped


@app.get("/")
def index() -> FileResponse:
    index_path = static / "index.html"
    if not index_path.exists():
        raise HTTPException(404, "dashboard missing")
    return FileResponse(index_path)


def _live_sut_status() -> dict[str, Any]:
    cfg = sut_settings()
    kind = str(cfg.get("kind") or "twin")
    base_url = str(cfg.get("base_url") or "")
    reachable = kind != "http"
    if kind == "http" and base_url:
        try:
            import httpx

            response = httpx.get(f"{base_url.rstrip('/')}/health", timeout=1.5)
            reachable = response.status_code == 200
        except Exception:
            reachable = False
    return {
        "kind": kind,
        "base_url": base_url,
        "reachable": reachable,
        "label": "Live HTTP agent" if kind == "http" else "In-process twin (mock)",
    }


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "seeds": len(_catalog.seeds),
        "campaigns": len(_catalog.campaigns),
        "personas": len(_catalog.personas),
        "sut": _live_sut_status(),
    }


@app.get("/api/portal")
def portal() -> dict[str, Any]:
    payload = portal_payload()
    payload["sut"] = _live_sut_status()
    payload["seeds"] = len(_catalog.seeds)
    return payload


@app.post("/api/sut")
def set_sut(req: SutRequest) -> dict[str, Any]:
    kind = req.kind.strip().lower()
    if kind not in {"twin", "http"}:
        raise HTTPException(400, "kind must be twin or http")
    cfg = sut_settings()
    if kind == "http":
        set_sut_override({"kind": "http", "base_url": cfg.get("base_url") or "http://127.0.0.1:8090"})
    else:
        set_sut_override({"kind": "twin"})
    status = _live_sut_status()
    if kind == "http" and not status["reachable"]:
        set_sut_override({"kind": "twin"})
        raise HTTPException(
            503,
            "Live SUT is not running. In another terminal run `aegis-red demo-sut`, "
            "or restart with `aegis-red try`.",
        )
    return status


@app.get("/api/taxonomy")
def taxonomy() -> dict[str, Any]:
    return _catalog.taxonomy


@app.get("/api/personas")
def personas() -> list[dict[str, Any]]:
    return [p.model_dump(by_alias=True) for p in _catalog.personas.values()]


@app.get("/api/seed-form")
def seed_form() -> dict[str, Any]:
    return form_options()


@app.get("/api/seeds")
def seeds() -> list[dict[str, Any]]:
    return [
        {
            "id": s.id,
            "coverage_key": s.coverage_key,
            "journey": s.journey,
            "step": s.step,
            "pillar": s.pillar.value,
            "family": s.family,
            "persona": s.persona,
            "title": s.title,
            "severity": s.severity,
            "topology": s.topology.value,
            "from_form": getattr(s, "source", None) == "ui",
        }
        for s in _catalog.seeds.values()
    ]


@app.post("/api/seeds")
def create_seed(req: SeedFormRequest) -> dict[str, Any]:
    try:
        seed = save_seed(_catalog, req.model_dump())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        "id": seed.id,
        "title": seed.title,
        "area": seed.family,
        "saved": True,
        "message": "Test saved. You can run it now or run every test.",
    }


@app.get("/api/campaigns")
def campaigns() -> list[dict[str, Any]]:
    return [
        {
            "id": c.id,
            "title": c.title,
            "use_case": c.use_case,
            "env": c.env.value,
            "sut_mode": c.sut_mode,
            "topology": c.topology.value,
            "seeds": c.select.seed_ids,
        }
        for c in _catalog.campaigns.values()
    ]


@app.post("/api/engagements/run")
def run_engagement(req: RunRequest) -> dict[str, Any]:
    if req.campaign_id not in _catalog.campaigns:
        raise HTTPException(404, f"unknown campaign {req.campaign_id}")
    return _run_and_score(req.campaign_id, sut_mode=req.sut_mode, env=req.env)


@app.post("/api/engagements/run-all")
def run_all(req: RunAllRequest | None = None) -> dict[str, Any]:
    req = req or RunAllRequest()
    if "all_tests" not in _catalog.campaigns:
        raise HTTPException(404, "all_tests campaign missing")
    return _run_and_score("all_tests", sut_mode=req.sut_mode, env=req.env)


@app.post("/api/engagements/run-one")
def run_one(req: RunOneRequest) -> dict[str, Any]:
    if req.seed_id not in _catalog.seeds:
        raise HTTPException(404, "unknown test")
    return _run_and_score("all_tests", sut_mode=req.sut_mode, env=req.env, seed_ids=[req.seed_id])


@app.get("/api/engagements")
def list_engagements() -> list[dict[str, Any]]:
    out = []
    for eid in _lake.list_engagements():
        try:
            summary = _lake.load_summary(eid)
        except FileNotFoundError:
            continue
        try:
            summary["results"] = _lake.load_results(eid)
        except FileNotFoundError:
            summary["results"] = None
        out.append(summary)
    out.sort(key=lambda row: row.get("started_at") or "", reverse=True)
    return out


@app.get("/api/engagements/{engagement_id}")
def get_engagement(engagement_id: str) -> dict[str, Any]:
    try:
        summary = _lake.load_summary(engagement_id)
        coverage = _lake.load_coverage(engagement_id)
        bundles = _lake.load_all_bundles(engagement_id)
    except FileNotFoundError as exc:
        raise HTTPException(404, "engagement not found") from exc
    try:
        results = _lake.load_results(engagement_id)
    except FileNotFoundError:
        results = _capture_results(engagement_id)
    _attach_transcripts(results.get("rows") or [], bundles)
    return {"summary": summary, "coverage": coverage, "bundles": bundles, "results": results}


@app.get("/api/engagements/{engagement_id}/coverage")
def get_coverage(engagement_id: str) -> list[dict[str, Any]]:
    try:
        return _lake.load_coverage(engagement_id)
    except FileNotFoundError as exc:
        raise HTTPException(404, "engagement not found") from exc


@app.get("/api/engagements/{engagement_id}/results.csv")
def download_results(engagement_id: str) -> FileResponse:
    path = _lake.results_csv_path(engagement_id)
    if not path.exists():
        try:
            _capture_results(engagement_id)
        except FileNotFoundError as exc:
            raise HTTPException(404, "engagement not found") from exc
    if not path.exists():
        raise HTTPException(404, "results not found")
    return FileResponse(path, filename=f"{engagement_id}-results.csv", media_type="text/csv")


@app.get("/api/engagements/{engagement_id}/evidence/{run_id}")
def get_bundle(engagement_id: str, run_id: str) -> dict[str, Any]:
    try:
        return _lake.load_bundle(engagement_id, run_id)
    except FileNotFoundError as exc:
        raise HTTPException(404, "bundle not found") from exc
