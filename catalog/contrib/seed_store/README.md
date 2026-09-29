# Seed store (contrib)

Community coverage pack. Add YAML seeds here so the engine and tester UI pick them up without core code changes.

**Good first issue:** pick a `CONTRIB-<AREA>-<nnn>` id, describe an intent (no payloads), list it in `campaigns/seed_store.yaml`. See the GitHub “Add a community seed” template.

## Rules

1. **Intent, not a recipe.** Say what the bad actor wants. Do not paste jailbreak payloads, exploit steps, or tool-call sequences.
2. **Oracles required.** Every seed needs `success_for_bank` and `failure_for_bank` names that exist in the oracle registry.
3. **IDs.** Use `CONTRIB-<AREA>-<nnn>` so they do not collide with `CORE-` or `DOM-`.
4. **Optional policy intercept.** Add `policy_intercept` or a new row in `extensions/policy_intercepts.yaml` (claim + which tools must stay denied).
5. **List the seed** in `campaigns/seed_store.yaml` or a new campaign.

See `CONTRIBUTING.md` in the repo root.
