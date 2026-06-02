#!/usr/bin/env python3
"""Validate basic structure for Skill directories in this repository."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONT_MATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)


def parse_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError("missing YAML front matter delimited by ---")

    data: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid front matter line: {line!r}")
        key, value = line.split(":", 1)
        value = value.strip().strip('"').strip("'")
        data[key.strip()] = value
    return data


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    rel_path = path.relative_to(ROOT)

    try:
        metadata = parse_front_matter(path)
    except ValueError as exc:
        return [f"{rel_path}: {exc}"]

    name = metadata.get("name", "")
    description = metadata.get("description", "")

    if not name:
        errors.append(f"{rel_path}: missing required front matter field 'name'")
    elif not SKILL_NAME_RE.fullmatch(name):
        errors.append(
            f"{rel_path}: name must use lowercase letters, numbers, and hyphens: {name!r}"
        )

    if not description:
        errors.append(f"{rel_path}: missing required front matter field 'description'")
    elif len(description) < 40:
        errors.append(f"{rel_path}: description should be at least 40 characters")

    if path.parent.name.startswith("."):
        errors.append(f"{rel_path}: skill directory should not be hidden")

    return errors


def find_tracked_generated_cache_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT, text=False
    )
    tracked_files = [
        ROOT / item.decode("utf-8")
        for item in output.split(b"\0")
        if item
    ]
    return [
        path
        for path in tracked_files
        if path.exists() and ("__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"})
    ]


def main() -> int:
    skill_files = sorted(
        path for path in ROOT.rglob("SKILL.md") if ".git" not in path.parts
    )
    errors: list[str] = []

    if not skill_files:
        errors.append("No SKILL.md files found")

    for skill_file in skill_files:
        errors.extend(validate_skill(skill_file))

    for cache_path in find_tracked_generated_cache_files():
        errors.append(
            f"{cache_path.relative_to(ROOT)}: generated Python cache should not be committed"
        )

    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_files)} skill file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
