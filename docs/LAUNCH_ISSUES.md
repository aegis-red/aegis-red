# Issues to open on launch

Paste each block into GitHub Issues. Use labels `good first issue` plus the extra label noted.

---

**Title:** `[seed] CONTRIB-PRIVACY-010 — refuse another-tenant secret`

**Labels:** `good first issue`, `seed-store`

Add a YAML seed under `catalog/contrib/seed_store/seeds/` whose **intent** is “do not disclose another tenant’s simulated secret.” No jailbreak payload. List the id in `campaigns/seed_store.yaml`. Oracles must already exist (`no_secret_in_output` / `no_cross_tenant`).

---

**Title:** `[seed] CONTRIB-HALL-010 — do not invent an unpublished status`

**Labels:** `good first issue`, `seed-store`

Intent-only seed: user asks for a status code that is not in fixtures. Secure twin must not emit the hallucination marker. Add to `seed_store` campaign.

---

**Title:** `[intercept] Claim write tools are allowed — must stay denied`

**Labels:** `good first issue`, `policy`

Add a row to `catalog/contrib/seed_store/extensions/policy_intercepts.yaml` (claim + `expand` tools). Point a `CONTRIB-` seed at it. Secure mode must hold; do not contribute a bypass.

---

**Title:** `[docs] Confirm Windows quickstart on a clean machine`

**Labels:** `good first issue`

Run `scripts/quickstart-windows.ps1` on a PC with only Python 3.11+ and git. File gaps (PATH, `py -3`, execution policy) as a PR to the script or Get started copy.

---

**Title:** `[docs] Confirm macOS quickstart on a clean machine`

**Labels:** `good first issue`

Run `scripts/quickstart-mac.sh` without a pre-existing venv. Note Python.org vs Homebrew `python3` issues in a PR.

---

**Title:** `[adapter] Document HTTP turn contract with a tiny example client`

**Labels:** `help wanted`, `adapter`

Without exploit payloads: show a 20-line `httpx` POST to `/v1/assurance/turn` against `aegis-red demo-sut`. Link from CONTRIBUTING.md.

---

**Title:** `[pack] Skeleton for a non-banking domain pack`

**Labels:** `help wanted`

Copy `catalog/domains/banking` structure to `catalog/domains/_template/` with empty fixtures and one CORE-overlapping seed pointing at core oracles. Do not invent a regulated industry’s real data.

---

**Title:** `[portal] Shorten Get started copy for UAT-only readers`

**Labels:** `good first issue`

UAT path should be three sentences: open Try now, save a seed, download CSV. Engineers keep the clone commands.
