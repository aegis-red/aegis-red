from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from aegis_red.catalog import Catalog
from aegis_red.evidence import EvidenceLake
from aegis_red.runner import CampaignRunner

app = typer.Typer(help="Aegis Red — authorized AI-agent assurance harness (open source)")
console = Console()


def _start_demo_sut(host: str, port: int) -> None:
    import threading
    import time

    import httpx
    import uvicorn

    from aegis_red.runtime import set_sut_override

    def _run() -> None:
        uvicorn.run("aegis_red.demo_sut:app", host=host, port=port, log_level="warning")

    threading.Thread(target=_run, daemon=True).start()
    url = f"http://{host}:{port}/health"
    for _ in range(80):
        try:
            if httpx.get(url, timeout=0.25).status_code == 200:
                set_sut_override({"kind": "http", "base_url": f"http://{host}:{port}"})
                console.print(f"[green]Live demo SUT[/green]  {url}")
                return
        except httpx.HTTPError:
            time.sleep(0.05)
    console.print(
        "[yellow]Demo SUT is still starting. Portal will use the twin until http://{host}:{port}/health is up.[/yellow]".format(
            host=host, port=port
        )
    )


def _open_portal(url: str) -> None:
    try:
        import webbrowser

        webbrowser.open(url)
    except Exception:
        pass


@app.command("catalog")
def show_catalog() -> None:
    cat = Catalog()
    table = Table(title="Aegis Red catalog")
    table.add_column("Kind")
    table.add_column("Count")
    table.add_row("Personas", str(len(cat.personas)))
    table.add_row("Seeds", str(len(cat.seeds)))
    table.add_row("Campaigns", str(len(cat.campaigns)))
    table.add_row("Journeys", str(len(cat.journeys)))
    console.print(table)

    seeds = Table(title="Seeds")
    seeds.add_column("ID")
    seeds.add_column("Journey / step")
    seeds.add_column("Persona")
    seeds.add_column("Coverage")
    for seed in cat.seeds.values():
        seeds.add_row(seed.id, f"{seed.journey}/{seed.step}", seed.persona, seed.coverage_key)
    console.print(seeds)


@app.command("run")
def run_campaign(
    campaign: str = typer.Argument(..., help="Campaign id, e.g. preprod_card_cert"),
    sut_mode: Optional[str] = typer.Option(None, help="Override SUT mode: secure | leaky"),
    env: Optional[str] = typer.Option(None, help="Override env: lower | uat | prod"),
) -> None:
    runner = CampaignRunner()
    summary = runner.run(campaign, sut_mode=sut_mode, env=env)
    table = Table(title=f"Engagement {summary.engagement_id}")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Campaign", summary.campaign_id)
    table.add_row("Use case", summary.use_case)
    table.add_row("SUT", summary.sut_mode)
    table.add_row("Topology", summary.topology.value)
    table.add_row("Bundles", str(summary.bundle_count))
    table.add_row("Coverage complete", str(summary.coverage_complete))
    table.add_row("Outcomes", str(summary.outcomes))
    table.add_row("Go / no-go", summary.go_no_go)
    table.add_row("Chain hash", summary.chain_hash[:16] + "…")
    console.print(table)
    if summary.go_no_go == "no-go":
        raise typer.Exit(code=2)


@app.command("coverage")
def show_coverage(engagement_id: str) -> None:
    lake = EvidenceLake()
    cells = lake.load_coverage(engagement_id)
    table = Table(title=f"Coverage {engagement_id}")
    table.add_column("Seed")
    table.add_column("Key")
    table.add_column("Persona")
    table.add_column("Outcome")
    table.add_column("Hash")
    for cell in cells:
        table.add_row(
            cell["seed_id"],
            cell["coverage_key"],
            f"{cell['persona']} ({cell['persona_class']})",
            cell["outcome"],
            cell["bundle_hash"][:12],
        )
    console.print(table)


@app.command("extensions")
def show_extensions() -> None:
    from aegis_red.extensions import list_extensions

    info = list_extensions()
    table = Table(title="Aegis Red extensions")
    table.add_column("Kind")
    table.add_column("Value")
    table.add_row("Packs", str(len(info["packs"])))
    table.add_row("Pack intercepts", ", ".join(info["pack_intercepts"]) or "—")
    table.add_row("SUT plugins", ", ".join(info["sut_plugins"]) or "twin (built-in)")
    table.add_row("Oracle plugins", ", ".join(info["oracle_plugins"]) or "—")
    console.print(table)
    packs = Table(title="Pack roots")
    packs.add_column("Path")
    for path in info["packs"]:
        packs.add_row(path)
    console.print(packs)


@app.command("demo-sut")
def demo_sut(
    host: str = "127.0.0.1",
    port: int = 8090,
) -> None:
    """Run the live demo agent (HTTP). Pair with sut.kind: http or `aegis-red try`."""
    import uvicorn

    console.print(f"Live demo SUT  http://{host}:{port}/health")
    uvicorn.run("aegis_red.demo_sut:app", host=host, port=port, reload=False)


@app.command("doctor")
def doctor() -> None:
    """Check packs, Python, and whether a live SUT is reachable — for contributors, UAT, and engineers."""
    import sys

    import httpx

    from aegis_red.extensions import list_extensions
    from aegis_red.runtime import sut_settings

    cat = Catalog()
    cfg = sut_settings()
    table = Table(title="Aegis Red doctor")
    table.add_column("Check")
    table.add_column("Value")
    table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    table.add_row("Seeds", str(len(cat.seeds)))
    table.add_row("Campaigns", str(len(cat.campaigns)))
    table.add_row("Packs", str(len(list_extensions()["packs"])))
    table.add_row("SUT kind", str(cfg.get("kind") or "twin"))
    table.add_row("SUT URL", str(cfg.get("base_url") or "—"))
    live = "n/a (twin)"
    if str(cfg.get("kind")) == "http":
        url = str(cfg.get("base_url") or "").rstrip("/")
        try:
            response = httpx.get(f"{url}/health", timeout=2.0)
            live = "reachable" if response.status_code == 200 else f"HTTP {response.status_code}"
        except httpx.HTTPError:
            live = "not reachable — run `aegis-red demo-sut` or `aegis-red try`"
    table.add_row("Live SUT", live)
    console.print(table)
    console.print("Portal: [bold]aegis-red try[/bold] then open http://127.0.0.1:8080")


@app.command("serve")
def serve(
    host: str = "127.0.0.1",
    port: int = 8080,
    live_sut: bool = typer.Option(False, "--live-sut", help="Also start the live demo agent"),
    sut_port: int = typer.Option(8090, "--sut-port", help="Port for the live demo agent"),
    open_browser: bool = typer.Option(False, "--open", help="Open the portal in a browser"),
) -> None:
    """Open the public portal. Use --live-sut so engineers can hit a real HTTP agent."""
    import uvicorn

    if live_sut:
        _start_demo_sut(host, sut_port)
    url = f"http://{host}:{port}"
    console.print(f"[bold]Portal[/bold]         {url}")
    console.print("UAT: add a seed on Try now. Engineers: live SUT is on --sut-port when --live-sut is set.")
    if open_browser:
        _open_portal(url)
    uvicorn.run("aegis_red.api:app", host=host, port=port, reload=False)


@app.command("try")
def try_portal(
    host: str = "127.0.0.1",
    port: int = 8080,
    sut_port: int = 8090,
) -> None:
    """One command for contributors, UAT, and engineers: portal + live demo SUT."""
    serve(host=host, port=port, live_sut=True, sut_port=sut_port, open_browser=True)


if __name__ == "__main__":
    app()
