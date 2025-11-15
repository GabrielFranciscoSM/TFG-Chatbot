#!/usr/bin/env python3
"""Simple helper to bump or set the version in pyproject.toml.

Usage:
  bump_version.py [--part patch|minor|major] [--version X.Y.Z]

If --version is provided, the script will set that version. Otherwise it bumps the
requested part (default: patch).

The script updates the file in-place and prints the new version to stdout.
"""

import argparse
import re
import sys
from pathlib import Path

SEMVER_RE = re.compile(
    r'(?m)^\s*(version\s*=\s*")(?P<maj>\d+)\.(?P<min>\d+)\.(?P<patch>\d+)(?P<quote>")'
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--part", choices=("patch", "minor", "major"), default="patch")
    p.add_argument("--version", help="Explicit version to set (format X.Y.Z)")
    p.add_argument(
        "--file",
        default=None,
        help="Path to pyproject.toml (defaults to repo root pyproject.toml)",
    )
    return p.parse_args()


def load_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def find_version(text: str):
    m = SEMVER_RE.search(text)
    if not m:
        return None
    return int(m.group("maj")), int(m.group("min")), int(m.group("patch"))


def replace_version(text: str, new_version: str) -> str:
    def repl(m):
        # m.group(1) is the prefix up to the opening quote (including it),
        # use the named 'quote' group to preserve the original quote char.
        return f"{m.group(1)}{new_version}{m.group('quote')}"

    new_text, n = SEMVER_RE.subn(repl, text, count=1)
    if n == 0:
        raise RuntimeError("Could not find a version line to replace in pyproject.toml")
    return new_text


def main():
    args = parse_args()
    # Determine pyproject path relative to this script: ../pyproject.toml
    if args.file:
        py_path = Path(args.file)
    else:
        py_path = Path(__file__).resolve().parents[1] / "pyproject.toml"

    if not py_path.exists():
        print(f"pyproject.toml not found at {py_path}", file=sys.stderr)
        sys.exit(2)

    text = load_file(py_path)
    cur = find_version(text)
    if cur is None:
        print("No version entry found in pyproject.toml", file=sys.stderr)
        sys.exit(3)

    if args.version:
        if not re.match(r"^\d+\.\d+\.\d+$", args.version):
            print("Invalid version format; expected X.Y.Z", file=sys.stderr)
            sys.exit(4)
        new_version = args.version
    else:
        maj, mino, patch = cur
        if args.part == "patch":
            patch += 1
        elif args.part == "minor":
            mino += 1
            patch = 0
        elif args.part == "major":
            maj += 1
            mino = 0
            patch = 0
        new_version = f"{maj}.{mino}.{patch}"

    new_text = replace_version(text, new_version)
    write_file(py_path, new_text)
    print(new_version)


if __name__ == "__main__":
    main()
