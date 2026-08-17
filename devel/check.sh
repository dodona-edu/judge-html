#!/bin/bash
set -euo pipefail

ROOT="$(dirname "$(dirname "$0")")"

cd "$ROOT"

ruff check .
ruff format --check .

# Only these paths are type-checked for now. validators/ and utils/ still carry about
# 100 diagnostics between them, so they opt in later, package by package.
# --python is required: CI has no .venv and no activated venv, so without
# it ty resolves based on what's available, which varies by machine.
ty check --python "$(command -v python3)" html_judge.py dodona/ exceptions/ decorators/
