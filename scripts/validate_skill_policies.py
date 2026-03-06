#!/usr/bin/env python3
"""Validate policy consistency across OpenClaw nutrition skill documents.

This is a lightweight guardrail so policy regressions are caught as code-level checks,
not only by human review.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require_contains(content: str, expected: str, label: str, errors: list[str]) -> None:
    if expected not in content:
        errors.append(f"[{label}] missing required text: {expected!r}")


def main() -> int:
    errors: list[str] = []

    skill = read("SKILL.md")
    logging_rules = read("references/logging_rules.md")
    privacy = read("references/privacy_security.md")

    # Confirmation-first behavior should stay explicit at both policy layers.
    require_contains(
        skill,
        "Confirm the final interpreted meal details before writing (explicit user confirmation required).",
        "SKILL.md",
        errors,
    )
    require_contains(
        logging_rules,
        "Confirm final meal details with the user before every append",
        "references/logging_rules.md",
        errors,
    )

    # Network usage policy: local-by-default + consent gate for image analysis.
    require_contains(
        privacy,
        "Default behavior is fully local file I/O only.",
        "references/privacy_security.md",
        errors,
    )
    require_contains(
        privacy,
        "Image-based nutrition estimation may use a connected model/network only after explicit user consent.",
        "references/privacy_security.md",
        errors,
    )
    require_contains(
        skill,
        "If input is an image, request explicit approval for online analysis first.",
        "SKILL.md",
        errors,
    )

    if errors:
        print("Policy validation failed:\n")
        for item in errors:
            print(f"- {item}")
        return 1

    print("Policy validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
