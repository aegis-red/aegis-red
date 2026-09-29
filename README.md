# Aegis Red

[![CI](https://github.com/aegis-red/aegis-red/actions/workflows/ci.yml/badge.svg)](https://github.com/aegis-red/aegis-red/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

Open-source **authorized** assurance harness for AI applications and agents.

**Core** covers Tech / AI safety (injection, hallucination, privacy, tools, summarization, memory, swarm isolation).  
**Domain packs** add a vertical. **Banking** is the first pack. **Community seeds** live in `catalog/contrib/seed_store`.

Aegis is a **platform**, not an unsupervised attacker. Seeds are intents, fixtures, and oracles — not exploit recipes. License: **Apache-2.0** (copyright **rfintek Inc.**). Catalog and contributions are **source in git** (YAML), not a database. Public project: [github.com/aegis-red/aegis-red](https://github.com/aegis-red/aegis-red).

## The problem

Agents can leak secrets, invent facts, honor a fake policy, or call tools they were never granted. Teams need Pass/Fail evidence without publishing a jailbreak cookbook.

## Try it (few clicks)

You do **not** need a bank agent. The portal can mock-test against an in-process twin, or hit a **live HTTP demo SUT**.

Clone into a folder named `aegis-red` (no spaces).

### macOS

```bash
git clone https://github.com/aegis-red/aegis-red.git
cd aegis-red
chmod +x scripts/quickstart-mac.sh
./scripts/quickstart-mac.sh
```

### Windows

```powershell
git clone https://github.com/aegis-red/aegis-red.git
cd aegis-red
powershell -ExecutionPolicy Bypass -File scripts\quickstart-windows.ps1
```

Then open **http://127.0.0.1:8080**

| Audience | What to do in the portal |
|---|---|
| UAT / QA | **Try now** → add 1–2 tests in plain language → Run this test → download Pass/Fail CSV |
| Individual contributor | **Contribute** for starter issues; add YAML in the seed store |
| Engineer | **Get started**, then on Try now switch on **live HTTP demo agent** |

Already cloned:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
aegis-red doctor
aegis-red try               # portal + live demo SUT, opens the browser
```

`aegis-red try` starts the portal on port 8080 and a live demo agent on port 8090.

## How we test AI

| Area | What a seed proves |
|---|---|
| Content safety | Harmful asks are refused |
| Prompt injection / instruction integrity | Official policy stays bound |
| Hallucination / grounding | Unpublished facts are not invented |
| Cross-tenant privacy | Other tenants' secrets stay closed |
| Tool contract | Denied tools stay denied |
| Policy robustness | A claimed policy rewrite does not grant tools or wires |
| Memory ≠ policy | Memory is not authorization |
| Swarm isolation | Peers cannot tailgate privilege |
| Evidence / lineage | Hashed bundles: harness sent vs agent reply |

Banking pack (optional): KYC, cards, wires, legal, compliance, risk, marketing, audit.

This is **not** Garak/Promptfoo/PyRIT: those probe models with attack corpora. Aegis scores an authorized agent against oracles and hashed evidence. Seeds describe intent; they are not an exploit cookbook.

## Live SUT

Default `sut.kind` is `twin` (in-process mock). For a real HTTP hop:

```yaml
# aegis.yaml
sut:
  kind: http
  base_url: http://127.0.0.1:8090
```

Or leave YAML as `twin` and run `aegis-red try` / toggle **Use live HTTP demo agent** in the portal.

Your own agent: register `aegis_red.sut` and implement `handle(seed, persona, utterance) -> Turn`. See `CONTRIBUTING.md`.

## Packs (`aegis.yaml`)

```yaml
packs:
  - id: core
    path: catalog/core
  - id: banking
    path: catalog/domains/banking
  - id: seed_store
    path: catalog/contrib/seed_store
```

```bash
aegis-red extensions
aegis-red run core_safety
aegis-red run seed_store
aegis-red serve              # portal only (twin)
aegis-red serve --live-sut   # portal + live agent
```

`go` exits 0. `no-go` (critical breach) exits 2.

## Contribute

Public starter work is listed in the portal (**Contribute**), GitHub issue templates, and `docs/LAUNCH_ISSUES.md`.

- Add a `CONTRIB-…` seed (intent only)
- Add a policy intercept (claim + tools that must stay denied)
- Start another domain pack
- Connect a live agent adapter
- Improve Mac/Windows setup or portal copy

Read `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and `docs/PUBLISH.md` before opening a PR.

## Tests

```bash
pytest
```
