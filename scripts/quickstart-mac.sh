#!/usr/bin/env bash
# One-script start for macOS: venv, install, portal + live demo SUT.
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.11+ is required. Install it from https://www.python.org/downloads/"
  exit 1
fi
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip
pip install -e ".[dev]"
echo
echo "Portal:     http://127.0.0.1:8080"
echo "Live SUT:   http://127.0.0.1:8090/health"
echo "UAT:        open Try now, add a seed, run it."
echo
exec aegis-red try
