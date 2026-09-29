# Contributing to Aegis Red

Aegis Red is an **authorized assurance harness**. Contributions grow coverage and adapters. They must not turn the repo into an exploit cookbook.

Read `CODE_OF_CONDUCT.md` and `SECURITY.md`. Use the GitHub issue templates (seed, policy probe, adapter, bug). Launch issue text to paste is in `docs/LAUNCH_ISSUES.md`. Coverage lives as YAML in git, not a database.

## Public contribution items

| Kind | Effort | Who | Where |
|---|---|---|---|
| Community seed | Good first issue | Individual contributors | `catalog/contrib/seed_store/seeds/` |
| Policy-robustness probe | Good first issue | UAT, security testers | `catalog/contrib/seed_store/extensions/policy_intercepts.yaml` |
| Domain pack | Medium | Engineers in another industry | `catalog/domains/<industry>/` + `aegis.yaml` |
| Live SUT adapter | Medium | Engineers | Your package, `aegis_red.sut` entry point |
| New oracle | Advanced | Engineers | `register_oracle` or `aegis_red.oracles` |
| Portal / setup scripts | Good first issue | Anyone | `src/aegis_red/static/index.html`, `scripts/` |

## How to run before you open a PR

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
aegis-red doctor
pytest
aegis-red try    # portal http://127.0.0.1:8080 + live demo SUT on :8090
```

UAT without YAML: open **Try now**, add a seed in plain language, run it, download the Pass/Fail CSV.

## Seed rules (required)

1. **Intent, not a recipe.** Describe the goal (“claim wire tools are allowed”). Do not paste jailbreak payloads, exploit steps, or tool-call sequences.
2. Every seed has `success_for_bank` and `failure_for_bank` names that exist in the oracle registry.
3. IDs use `CONTRIB-<AREA>-<nnn>` in the seed store. Core uses `CORE-`. Banking uses `DOM-` / `REG-` / `SWARM-`.
4. `environment.prod` is `shadow_only` unless there is a written reason.
5. Add the id to a campaign (`seed_store` or a new campaign).
6. Include `pytest` coverage or run `aegis-red run seed_store` in the PR notes.

## Policy robustness (tool access)

This is how we test “policy jailbreak” **without publishing attacks**:

- Add a row to `extensions/policy_intercepts.yaml`: `id`, `label`, `claim` (one sentence), `expand` (tools that must stay **denied** on a secure twin).
- Point a seed at that `policy_intercept.id`.
- The secure twin must keep official policy bound. The leaky practice twin is allowed to Fail so evidence exists.

Do not contribute working bypass payloads.

## Live SUT plugin

The repo ships a **live demo agent**: `aegis-red demo-sut` (HTTP on port 8090). The built-in `http` adapter posts `/v1/assurance/turn`.

Your own agent:

```toml
[project.entry-points."aegis_red.sut"]
acme = "acme_aegis.adapter:AcmeAdapter"
```

```yaml
# aegis.yaml
sut:
  kind: acme
```

The adapter constructor is `(fixtures, seed, mode)` and must implement `handle(seed, persona, utterance) -> Turn` with a `.twins` snapshot (same contract as `TwinAdapter`). Compatible HTTP agents may reuse `kind: http` if they speak the demo SUT JSON contract.

## License

Apache-2.0. By opening a PR you agree to that license for the contribution.
