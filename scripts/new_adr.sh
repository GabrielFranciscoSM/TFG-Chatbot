#!/usr/bin/env bash
set -euo pipefail

# Create a new ADR file in docs/ADR with a sequential number and open it for editing.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ADR_DIR="$ROOT_DIR/docs/ADR"
mkdir -p "$ADR_DIR"

TITLE="${*:-}"
if [ -z "$TITLE" ]; then
  echo "Usage: $0 \"Short title\""
  exit 1
fi

# Find last numbered ADR filename like 0001-...md
LAST=$(ls -1 "$ADR_DIR" 2>/dev/null | grep -E '^[0-9]{4}-' | sort | tail -n1 || true)
if [ -z "$LAST" ]; then
  NEXT=1
else
  # Extract number part before the hyphen
  NUM_PART=${LAST%%-*}
  NEXT=$((10#$NUM_PART + 1))
fi
NUM=$(printf "%04d" "$NEXT")

# Compute next nav_order by scanning existing ADR files that start with 4-digit prefix
EXISTING_NAVS=$(grep -h "^nav_order:" "$ADR_DIR"/[0-9][0-9][0-9][0-9]-*.md 2>/dev/null | awk '{print $2}' || true)
if [ -z "$EXISTING_NAVS" ]; then
  NEXT_NAV=1
else
  MAX_NAV=$(echo "$EXISTING_NAVS" | sort -n | tail -n1)
  NEXT_NAV=$((MAX_NAV + 1))
fi

SLUG=$(echo "$TITLE" | iconv -c -t ascii//TRANSLIT | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g' | sed -E 's/^-+|-+$//g')
FILE="$ADR_DIR/${NUM}-${SLUG}.md"

if [ -e "$FILE" ]; then
  echo "File already exists: $FILE"
  exit 1
fi

cat > "$FILE" <<EOF
---
adr: $NUM
title: "$TITLE"
date: $(date +%F)
status: Proposed
parent: Architecture Decision Records
nav_order: $NEXT_NAV
---

# ${NUM} - $TITLE

## Status

Proposed

## Context

Describe the context and reasons for the decision.

## Decision

State the decision made.

## Consequences

Describe the consequences (positive, negative, technical debt, work required).

## Alternatives considered

- Alternative 1
- Alternative 2

## References

Add links to issues, docs or notes.

EOF

echo "Created $FILE"

