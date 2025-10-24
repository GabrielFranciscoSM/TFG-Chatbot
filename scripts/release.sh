#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYPROJECT="$ROOT_DIR/pyproject.toml"
PY_BUMP="$ROOT_DIR/scripts/bump_version.py"

usage() {
  cat <<EOF
Usage: $(basename "$0") [--part patch|minor|major] [--version X.Y.Z] [--push] [--allow-dirty]

Defaults: --part patch

Options:
  --part    Which part to bump (patch,minior,major)
  --version Set an explicit version (overrides --part)
  --push    Push commit and tag to remote
  --allow-dirty Allow running even if working tree has uncommitted changes

Example:
  $(basename "$0") --part minor --push

EOF
}

PART="patch"
EXPLICIT_VERSION=""
PUSH=false
ALLOW_DIRTY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --part)
      PART="$2"; shift 2;;
    --version)
      EXPLICIT_VERSION="$2"; shift 2;;
    --push)
      PUSH=true; shift;;
    --allow-dirty)
      ALLOW_DIRTY=true; shift;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

if ! command -v git >/dev/null 2>&1; then
  echo "git not found in PATH" >&2
  exit 2
fi

if [[ ! -f "$PYPROJECT" ]]; then
  echo "pyproject.toml not found at $PYPROJECT" >&2
  exit 3
fi

if [[ "$ALLOW_DIRTY" != "true" ]]; then
  if [[ -n "$(git -C "$ROOT_DIR" status --porcelain)" ]]; then
    echo "Working tree is not clean. Commit or stash changes, or pass --allow-dirty to force." >&2
    exit 4
  fi
fi

if [[ -z "$EXPLICIT_VERSION" ]]; then
  NEW_VERSION=$(python3 "$PY_BUMP" --part "$PART" --file "$PYPROJECT")
else
  NEW_VERSION=$(python3 "$PY_BUMP" --version "$EXPLICIT_VERSION" --file "$PYPROJECT")
fi

echo "New version: $NEW_VERSION"

# Stage and commit
git -C "$ROOT_DIR" add "$PYPROJECT"
if git -C "$ROOT_DIR" diff --staged --quiet; then
  echo "No staged changes to commit. Exiting." >&2
  exit 5
fi

git -C "$ROOT_DIR" commit -m "Bump version to v$NEW_VERSION"
git -C "$ROOT_DIR" tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

if [[ "$PUSH" == "true" ]]; then
  git -C "$ROOT_DIR" push
  git -C "$ROOT_DIR" push --tags
fi

echo "Created tag v$NEW_VERSION and committed updated pyproject.toml"
