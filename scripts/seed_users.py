#!/usr/bin/env python3
"""
Seed script for creating initial users in the TFG Chatbot database.

This script creates admin, professor, and student users for development
and testing purposes. It uses the same password hashing as the backend.

Usage:
    # From the project root:
    python scripts/seed_users.py

    # Or with uv:
    uv run scripts/seed_users.py

    # With custom MongoDB URI:
    MONGO_URI=mongodb://user:pass@host:27017 python scripts/seed_users.py

Environment Variables:
    MONGO_URI: MongoDB connection string (optional, uses backend config by default)
    SEED_PASSWORD: Password for all seeded users (default: "admin123")
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

# Determine project root (parent of scripts/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the project root to the path so we can import backend modules
sys.path.insert(0, PROJECT_ROOT)


def _setup_environment() -> None:
    """Load .env and configure MongoDB hostname for local execution."""
    # Import here to avoid E402
    from dotenv import load_dotenv

    env_path = os.path.join(PROJECT_ROOT, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded environment from: {env_path}")

    # When running locally (not in Docker), use localhost instead of Docker hostname
    if not os.getenv("MONGO_URI") and os.getenv("MONGO_HOSTNAME") in ("mongo", None):
        os.environ["MONGO_HOSTNAME"] = "localhost"
        print("Using localhost for MongoDB (local execution)")


# Default seed users
SEED_USERS = [
    {
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "subjects": [],
    },
    {
        "username": "profesor",
        "email": "profesor@example.com",
        "role": "professor",
        "subjects": ["iv", "ic"],  # Infraestructura Virtual, Inteligencia Computacional
    },
    {
        "username": "profesor2",
        "email": "profesor2@example.com",
        "role": "professor",
        "subjects": ["so"],  # Sistemas Operativos
    },
    {
        "username": "estudiante",
        "email": "estudiante@example.com",
        "role": "student",
        "subjects": ["iv"],
    },
]


def seed_users(
    mongo_uri: str | None = None,
    db_name: str | None = None,
    password: str = "admin123",
    force: bool = False,
) -> dict[str, list[Any]]:
    """
    Seed the database with initial users.

    Args:
        mongo_uri: MongoDB connection URI (uses settings if not provided)
        db_name: Database name (uses settings if not provided)
        password: Password to set for all users
        force: If True, delete existing users before seeding

    Returns:
        Dict with results (created, skipped, errors)
    """
    # Import here after environment setup
    from pymongo import MongoClient

    from backend.config import Settings
    from backend.security import get_password_hash

    settings = Settings()

    # Use backend settings if not provided
    uri = mongo_uri or settings.get_mongo_uri()
    database = db_name or settings.db_name

    print(f"Connecting to MongoDB: {database}")
    client: MongoClient[dict[str, Any]] = MongoClient(uri)
    db = client[database]
    users_collection = db["users"]

    # Hash the password once (same for all users)
    hashed_password = get_password_hash(password)

    results: dict[str, list[Any]] = {"created": [], "skipped": [], "errors": []}

    if force:
        # Delete existing seed users
        for user_data in SEED_USERS:
            users_collection.delete_one({"username": user_data["username"]})
        print("Deleted existing seed users (--force mode)")

    for user_data in SEED_USERS:
        try:
            # Check if user already exists
            existing = users_collection.find_one({"username": user_data["username"]})
            if existing:
                print(f"  ⏭️  User '{user_data['username']}' already exists, skipping")
                results["skipped"].append(user_data["username"])
                continue

            # Create user document
            user_doc = {
                **user_data,
                "hashed_password": hashed_password,
            }

            users_collection.insert_one(user_doc)
            print(f"  ✅ Created user '{user_data['username']}' ({user_data['role']})")
            results["created"].append(user_data["username"])

        except Exception as e:
            print(f"  ❌ Error creating '{user_data['username']}': {e}")
            results["errors"].append(
                {"username": user_data["username"], "error": str(e)}
            )

    client.close()
    return results


def main() -> None:
    """Main entry point for the seed script."""
    # Setup environment first
    _setup_environment()

    parser = argparse.ArgumentParser(description="Seed the database with initial users")
    parser.add_argument(
        "--password",
        default=os.getenv("SEED_PASSWORD", "admin123"),
        help="Password for all seeded users (default: admin123)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete and recreate existing seed users",
    )
    parser.add_argument(
        "--mongo-uri",
        default=os.getenv("MONGO_URI"),
        help="MongoDB connection URI (uses backend config by default)",
    )

    args = parser.parse_args()

    print("=" * 50)
    print("TFG Chatbot - User Seeding Script")
    print("=" * 50)
    print()

    results = seed_users(
        mongo_uri=args.mongo_uri,
        password=args.password,
        force=args.force,
    )

    print()
    print("=" * 50)
    print("Summary:")
    print(f"  Created: {len(results['created'])}")
    print(f"  Skipped: {len(results['skipped'])}")
    print(f"  Errors:  {len(results['errors'])}")
    print("=" * 50)

    if results["created"]:
        print()
        print("Login credentials:")
        print(f"  Password for all users: {args.password}")
        print()
        print("  Users created:")
        for username in results["created"]:
            print(f"    - {username}")


if __name__ == "__main__":
    main()
