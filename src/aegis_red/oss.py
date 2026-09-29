"""Public clone identity for README, portal, and setup copy.

GitHub org and repo are the product brand (aegis-red). Copyright is rfintek Inc.
Override the org with AEGIS_OSS_ORG if you fork.
"""

from __future__ import annotations

import os

REPO_NAME = "aegis-red"
ORG = os.environ.get("AEGIS_OSS_ORG", "aegis-red")


def github_repo() -> str:
    return f"https://github.com/{ORG}/{REPO_NAME}"


def clone_url() -> str:
    return f"{github_repo()}.git"


def issues_url() -> str:
    return f"{github_repo()}/issues"


def security_advisory_url() -> str:
    return f"{github_repo()}/security/advisories/new"


def mac_command() -> str:
    return (
        f"git clone {clone_url()}\n"
        f"cd {REPO_NAME}\n"
        "chmod +x scripts/quickstart-mac.sh\n"
        "./scripts/quickstart-mac.sh"
    )


def windows_command() -> str:
    return (
        f"git clone {clone_url()}\n"
        f"cd {REPO_NAME}\n"
        r"powershell -ExecutionPolicy Bypass -File scripts\quickstart-windows.ps1"
    )


def mac_steps() -> list[str]:
    return [
        "Install Python 3.11+ from python.org if `python3 --version` fails.",
        f"git clone {clone_url()} && cd {REPO_NAME}",
        "chmod +x scripts/quickstart-mac.sh && ./scripts/quickstart-mac.sh",
        "Open http://127.0.0.1:8080 — the portal and a live demo agent start together.",
    ]


def windows_steps() -> list[str]:
    return [
        "Install Python 3.11+ from python.org and tick Add python.exe to PATH.",
        f"git clone {clone_url()} ; cd {REPO_NAME}",
        "powershell -ExecutionPolicy Bypass -File scripts/quickstart-windows.ps1",
        "Open http://127.0.0.1:8080 — the portal and a live demo agent start together.",
    ]
