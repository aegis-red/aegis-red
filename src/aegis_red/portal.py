"""Copy for the public portal: problem, AI coverage, setup, contribution items."""

from __future__ import annotations

from typing import Any

from aegis_red.oss import mac_command, mac_steps, windows_command, windows_steps

PILLARS = [
    {
        "id": "content_safety",
        "title": "Content safety",
        "who": "Everyone",
        "how": "Seeds ask for harmful or disallowed help. A secure agent must refuse. Pass = hold.",
    },
    {
        "id": "injection",
        "title": "Prompt injection & instruction integrity",
        "who": "Engineers, UAT",
        "how": "Seeds try to override system instructions. Official policy must stay bound.",
    },
    {
        "id": "hallucination",
        "title": "Hallucination / grounding",
        "who": "Engineers, UAT",
        "how": "Seeds ask for unpublished facts. The agent must not invent status codes or citations.",
    },
    {
        "id": "privacy",
        "title": "Cross-tenant privacy",
        "who": "Engineers, UAT",
        "how": "Seeds ask for another tenant's secrets. The agent must not disclose them.",
    },
    {
        "id": "tools",
        "title": "Tool contract",
        "who": "Engineers",
        "how": "Seeds claim extra tools. Denied tools stay denied on a secure SUT.",
    },
    {
        "id": "policy",
        "title": "Policy robustness",
        "who": "UAT, contributors",
        "how": "Optional intercept: a bad actor claims a policy rewrite. Official rules still hold.",
    },
    {
        "id": "memory",
        "title": "Memory ≠ policy",
        "who": "Engineers",
        "how": "Seeds put a fake rule in memory. Memory must not become authorization.",
    },
    {
        "id": "swarm",
        "title": "Swarm / privilege isolation",
        "who": "Engineers",
        "how": "Peer agents must not tailgate into privileged tools or money movement.",
    },
    {
        "id": "evidence",
        "title": "Evidence & lineage",
        "who": "UAT, auditors",
        "how": "Every run writes hashed bundles: what was sent, what the agent replied, tools, oracles.",
    },
    {
        "id": "domain",
        "title": "Domain packs (banking first)",
        "who": "UAT in a vertical",
        "how": "Optional pack: KYC, cards, wires, legal, compliance, risk, marketing, audit.",
    },
]

CONTRIBUTIONS = [
    {
        "id": "seed",
        "title": "Add a community seed",
        "effort": "Good first issue",
        "who": "Individual contributors",
        "where": "catalog/contrib/seed_store/seeds/",
        "steps": "Describe an intent in YAML. No jailbreak payloads. List the id in campaigns/seed_store.yaml.",
    },
    {
        "id": "intercept",
        "title": "Add a policy-robustness probe",
        "effort": "Good first issue",
        "who": "UAT, security testers",
        "where": "catalog/contrib/seed_store/extensions/policy_intercepts.yaml",
        "steps": "Add a claim plus tools that must stay denied. Point a seed at that intercept id.",
    },
    {
        "id": "pack",
        "title": "Start a domain pack",
        "effort": "Medium",
        "who": "Engineers in another industry",
        "where": "catalog/domains/<industry>/",
        "steps": "Copy the banking pack skeleton, add fixtures and a handful of seeds, list it in aegis.yaml.",
    },
    {
        "id": "adapter",
        "title": "Connect a live agent",
        "effort": "Medium",
        "who": "Engineers",
        "where": "Your package, entry point aegis_red.sut",
        "steps": "Implement handle(seed, persona, utterance) -> Turn and return a twins snapshot.",
    },
    {
        "id": "oracle",
        "title": "Add an oracle",
        "effort": "Advanced",
        "who": "Engineers",
        "where": "src/aegis_red/oracles.py or aegis_red.oracles entry point",
        "steps": "Name the check, evaluate twin state + tool spy, never encode an exploit recipe.",
    },
    {
        "id": "docs_ui",
        "title": "Improve the portal or setup scripts",
        "effort": "Good first issue",
        "who": "Anyone",
        "where": "src/aegis_red/static/index.html, scripts/",
        "steps": "Make UAT copy clearer, fix Windows/Mac steps, add a translation-friendly hint.",
    },
]


def portal_payload() -> dict[str, Any]:
    return {
        "product": "Aegis Red",
        "license": "Apache-2.0",
        "problem": (
            "AI applications and agents can leak secrets, invent facts, honor a fake policy, "
            "or call tools they were never granted. Teams need an authorized way to prove "
            "those failures do not happen — without publishing an exploit cookbook."
        ),
        "what_it_is": (
            "Aegis Red is an open-source assurance harness. You describe intents (seeds) and "
            "oracles. The harness talks to a system under test, records the transcript, and "
            "scores Pass or Fail against examiner-grade evidence."
        ),
        "what_it_is_not": (
            "It is not unsupervised jailbreaking. Seeds are intents and fixtures, not payloads. "
            "Do not contribute working bypass recipes."
        ),
        "audiences": [
            {
                "id": "contributor",
                "title": "Individual contributor",
                "do": "Add a seed or intercept in the seed store, or improve the portal.",
            },
            {
                "id": "uat",
                "title": "UAT / QA",
                "do": "Open the portal, add two plain-language tests, run them, download Pass/Fail CSV.",
            },
            {
                "id": "engineer",
                "title": "Engineer",
                "do": "Run the live demo SUT over HTTP, then point sut.kind at your own agent plugin.",
            },
        ],
        "pillars": PILLARS,
        "setup": {
            "mac": {"steps": mac_steps(), "command": mac_command()},
            "windows": {"steps": windows_steps(), "command": windows_command()},
            "mock": (
                "Already in the portal: open Try now, add a seed in plain language, run it. "
                "No clone required once someone has started `aegis-red try` on this machine."
            ),
        },
        "contributions": CONTRIBUTIONS,
    }
