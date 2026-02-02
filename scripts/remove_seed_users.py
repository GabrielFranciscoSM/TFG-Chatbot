#!/usr/bin/env python3
"""
Script to remove seed and test users from the database.

Usage:
    # From the project root:
    python scripts/remove_seed_users.py

    # With uv:
    uv run scripts/remove_seed_users.py

    # Dry run (show what would be deleted without deleting):
    uv run scripts/remove_seed_users.py --dry-run

    # Only remove test users (testuser_*, student1, etc.), keep seed users:
    uv run scripts/remove_seed_users.py --test-only

    # Remove all (seed + test users):
    uv run scripts/remove_seed_users.py --all
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Any

# Determine project root (parent of scripts/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


# Seed users to remove (matches seed_users.py)
SEED_USERNAMES = ["admin", "profesor", "profesor2", "estudiante"]

# Patterns for test users created by pytest
TEST_USER_PATTERNS = [
    r"^testuser_",  # testuser_<uuid>
    r"^integration_user_",  # integration_user_<uuid>
    r"^test_",  # test_<anything>
    r"^student\d+$",  # student1, student2, etc.
    r"^professor\d+$",  # professor1, professor2, etc.
    r"^admin\d+$",  # admin1, admin2, etc.
    r"_test$",  # anything ending in _test
]


def _setup_environment() -> None:
    """Load .env and configure MongoDB hostname for local execution."""
    from dotenv import load_dotenv

    env_path = os.path.join(PROJECT_ROOT, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded environment from: {env_path}")

    if not os.getenv("MONGO_URI") and os.getenv("MONGO_HOSTNAME") in ("mongo", None):
        os.environ["MONGO_HOSTNAME"] = "localhost"
        print("Using localhost for MongoDB (local execution)")


def _is_test_user(username: str) -> bool:
    """Check if a username matches test user patterns."""
    return any(re.match(pattern, username) for pattern in TEST_USER_PATTERNS)


def remove_seed_users(
    dry_run: bool = False,
    include_seeds: bool = True,
    include_tests: bool = True,
) -> dict[str, list[str]]:
    """
    Remove seed and/or test users from the database.

    Args:
        dry_run: If True, only show what would be deleted without deleting
        include_seeds: If True, remove hardcoded seed users
        include_tests: If True, remove users matching test patterns

    Returns:
        Dict with deleted usernames by category
    """
    from pymongo import MongoClient

    from backend.config import Settings

    settings = Settings()
    uri = settings.get_mongo_uri()
    database = settings.db_name

    print(f"Connecting to MongoDB: {database}")
    client: MongoClient[dict[str, Any]] = MongoClient(uri)
    db = client[database]
    users_collection = db["users"]

    results: dict[str, list[str]] = {
        "seed_deleted": [],
        "seed_not_found": [],
        "test_deleted": [],
    }

    # Remove seed users
    if include_seeds:
        print("\n📋 Seed users:")
        for username in SEED_USERNAMES:
            existing = users_collection.find_one({"username": username})
            if existing:
                if dry_run:
                    print(
                        f"  🔍 Would delete '{username}' ({existing.get('role', 'unknown')})"
                    )
                else:
                    users_collection.delete_one({"username": username})
                    print(f"  ✅ Deleted '{username}'")
                results["seed_deleted"].append(username)
            else:
                print(f"  ⏭️  '{username}' not found")
                results["seed_not_found"].append(username)

    # Remove test users (find all matching patterns)
    if include_tests:
        print("\n🧪 Test users:")
        all_users = users_collection.find({}, {"username": 1, "role": 1})
        test_users_found = []

        for user in all_users:
            username = user.get("username", "")
            if _is_test_user(username) and username not in SEED_USERNAMES:
                test_users_found.append(user)

        if not test_users_found:
            print("  No test users found")
        else:
            for user in test_users_found:
                username = user["username"]
                role = user.get("role", "unknown")
                if dry_run:
                    print(f"  🔍 Would delete '{username}' ({role})")
                else:
                    users_collection.delete_one({"username": username})
                    print(f"  ✅ Deleted '{username}'")
                results["test_deleted"].append(username)

    client.close()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove seed and test users from the database"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument(
        "--test-only",
        action="store_true",
        help="Only remove test users (testuser_*, student1, etc.), keep seed users",
    )
    parser.add_argument(
        "--seed-only",
        action="store_true",
        help="Only remove seed users, keep test users",
    )
    args = parser.parse_args()

    _setup_environment()

    # Determine what to remove
    include_seeds = not args.test_only
    include_tests = not args.seed_only

    mode = "DRY RUN" if args.dry_run else "REMOVE"
    scope = (
        "Test Users Only"
        if args.test_only
        else "Seed Users Only" if args.seed_only else "All (Seed + Test)"
    )

    print(f"\n{'='*50}")
    print(f"  {mode}: {scope}")
    print(f"{'='*50}")

    results = remove_seed_users(
        dry_run=args.dry_run,
        include_seeds=include_seeds,
        include_tests=include_tests,
    )

    print(f"\n{'='*50}")
    print("  Summary")
    print(f"{'='*50}")
    action = "Would delete" if args.dry_run else "Deleted"

    if include_seeds:
        print(f"  Seed users {action.lower()}: {len(results['seed_deleted'])}")
    if include_tests:
        print(f"  Test users {action.lower()}: {len(results['test_deleted'])}")

    total = len(results["seed_deleted"]) + len(results["test_deleted"])
    print(f"  Total: {total} users")

    if args.dry_run and total > 0:
        print("\n  Run without --dry-run to actually delete these users.")


if __name__ == "__main__":
    main()
