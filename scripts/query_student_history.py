#!/usr/bin/env python3
"""
Query student conversation history grouped by sessions.

Usage:
    python scripts/query_student_history.py <username>
    python scripts/query_student_history.py estudiante
    python scripts/query_student_history.py estudiante --json
    python scripts/query_student_history.py --list-users

Environment:
    Requires MONGO_URI or default MongoDB connection settings.
"""

import argparse
import json
import sys
from datetime import datetime

from pymongo import MongoClient

# Default MongoDB connection (matches docker-compose)
DEFAULT_MONGO_URI = "mongodb://root:example@localhost:27017"
DEFAULT_DB_NAME = "tfg_chatbot"


def get_mongo_client(uri: str = DEFAULT_MONGO_URI) -> MongoClient:
    """Create MongoDB client."""
    return MongoClient(uri)


def list_users_with_conversations(db) -> list[str]:
    """Get list of users who have conversations."""
    return db.conversations.distinct("user_id")


def get_student_history_by_sessions(db, user_id: str) -> list[dict]:
    """
    Query student conversation history grouped by sessions.

    Args:
        db: MongoDB database instance
        user_id: Username to query

    Returns:
        List of session documents with messages
    """
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$sort": {"timestamp": 1}},
        {
            "$group": {
                "_id": "$session_id",
                "subject": {"$first": "$subject"},
                "first_message": {"$first": "$timestamp"},
                "last_message": {"$last": "$timestamp"},
                "message_count": {"$sum": 1},
                "difficulties": {"$push": "$difficulty"},
                "messages": {
                    "$push": {
                        "timestamp": "$timestamp",
                        "query": "$query",
                        "answer": "$answer",
                        "difficulty": "$difficulty",
                        "was_test": "$was_test",
                        "latency_ms": "$latency_ms",
                        "rag_sources_used": "$rag_sources_used",
                    }
                },
            }
        },
        {"$sort": {"first_message": -1}},  # Most recent sessions first
    ]

    return list(db.conversations.aggregate(pipeline))


def format_session_output(session: dict, verbose: bool = False) -> str:
    """Format a session for human-readable output."""
    lines = []
    lines.append(f"📁 Session: {session['_id']}")
    lines.append(f"   Subject: {session['subject']}")
    lines.append(f"   Messages: {session['message_count']}")

    # Format timestamps
    first = session["first_message"]
    last = session["last_message"]
    if isinstance(first, datetime):
        first_str = first.strftime("%Y-%m-%d %H:%M:%S")
        last_str = last.strftime("%Y-%m-%d %H:%M:%S")
    else:
        first_str = str(first)
        last_str = str(last)
    lines.append(f"   Period: {first_str} → {last_str}")

    # Difficulty distribution
    difficulties = session.get("difficulties", [])
    diff_counts: dict[str, int] = {}
    for d in difficulties:
        diff_counts[d] = diff_counts.get(d, 0) + 1
    lines.append(f"   Difficulties: {diff_counts}")

    lines.append("   Conversation:")
    for i, msg in enumerate(session["messages"], 1):
        query = msg["query"]
        answer = msg["answer"] or ""
        # Truncate for display
        answer_preview = answer[:100] + "..." if len(answer) > 100 else answer
        answer_preview = answer_preview.replace("\n", " ")

        lines.append(f"     [{i}] Q: {query}")
        lines.append(f"         A: {answer_preview}")
        lines.append(f"         Difficulty: {msg['difficulty']}")

        if verbose:
            if msg.get("latency_ms"):
                lines.append(f"         Latency: {msg['latency_ms']:.0f}ms")
            if msg.get("was_test"):
                lines.append("         [TEST]")
            if msg.get("rag_sources_used"):
                lines.append(f"         RAG sources: {msg['rag_sources_used']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Query student conversation history by sessions"
    )
    parser.add_argument("username", nargs="?", help="Username to query")
    parser.add_argument(
        "--list-users", action="store_true", help="List users with conversations"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show more details"
    )
    parser.add_argument(
        "--mongo-uri", default=DEFAULT_MONGO_URI, help="MongoDB connection URI"
    )
    parser.add_argument("--db", default=DEFAULT_DB_NAME, help="Database name")

    args = parser.parse_args()

    # Connect to MongoDB
    try:
        client = get_mongo_client(args.mongo_uri)
        db = client[args.db]
        # Test connection
        db.command("ping")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}", file=sys.stderr)
        sys.exit(1)

    # List users mode
    if args.list_users:
        users = list_users_with_conversations(db)
        if args.json:
            print(json.dumps(users, indent=2))
        else:
            print("Users with conversations:")
            for user in users:
                count = db.conversations.count_documents({"user_id": user})
                print(f"  - {user} ({count} messages)")
        client.close()
        return

    # Require username for history query
    if not args.username:
        parser.error("Username required (or use --list-users)")

    # Query history
    sessions = get_student_history_by_sessions(db, args.username)

    if not sessions:
        print(f"No conversations found for user: {args.username}")
        client.close()
        return

    # Output
    if args.json:
        # Convert datetime objects for JSON serialization
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        print(json.dumps(sessions, indent=2, default=json_serial))
    else:
        print(f"=== Conversation History for '{args.username}' ===\n")
        print(f"Total sessions: {len(sessions)}")
        total_messages = sum(s["message_count"] for s in sessions)
        print(f"Total messages: {total_messages}\n")

        for session in sessions:
            print(format_session_output(session, verbose=args.verbose))
            print()

    client.close()


if __name__ == "__main__":
    main()
