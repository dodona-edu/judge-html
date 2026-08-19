#!/usr/bin/env python3
"""Check that requirements.txt matches what's actually installed in the judge image.

requirements.txt mirrors dodona-edu/docker-images/dodona-html.dockerfile: it documents what
ghcr.io/dodona-edu/dodona-html:latest ships, it isn't a source of truth that pip installs from
in production. The judge runs with whatever the image has installed, so if requirements.txt
drifts from the image, it starts lying about what's actually running.

This script can't inspect the image directly, so instead it relies on where it runs: in CI it
runs as a step inside a container built from that very image (see
.github/workflows/integration_test.yml), so "importable/installed in the current Python
environment" *is* "what the image ships" -- the actual source of truth. It parses
requirements.txt, looks up each pinned package's installed version via importlib.metadata, and
reports every mismatch (missing package or version drift) before exiting non-zero.
"""

import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

REQUIREMENTS_PATH = Path(__file__).resolve().parent.parent / "requirements.txt"


def parse_requirements(path: Path) -> dict[str, str]:
    """Parse a requirements.txt file into a mapping of package name to pinned version.

    Blank lines are skipped, inline `#` comments are stripped, and lines that are then
    empty are skipped too. Remaining lines are expected to be `name==version` pins.
    """
    pins: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        name, _, want = line.partition("==")
        pins[name.strip()] = want.strip()
    return pins


def find_mismatches(pins: dict[str, str]) -> list[str]:
    """Compare pinned versions against what's installed, returning a list of problem descriptions."""
    problems: list[str] = []
    for name, want in pins.items():
        try:
            have = version(name)
        except PackageNotFoundError:
            problems.append(f"{name}: pinned {want}, NOT INSTALLED in the image")
            continue
        if have != want:
            problems.append(f"{name}: requirements.txt says {want}, image has {have}")
    return problems


def main() -> None:
    pins = parse_requirements(REQUIREMENTS_PATH)
    problems = find_mismatches(pins)

    if problems:
        print("requirements.txt does not match the image:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        raise SystemExit(1)

    print(f"requirements.txt matches the {len(pins)} package(s) installed in the image.")


if __name__ == "__main__":
    main()
