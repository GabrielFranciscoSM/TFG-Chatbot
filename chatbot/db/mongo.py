import os
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


class MongoDBClient:
    """Simple MongoDB helper to connect, get collections and perform common ops.

    Usage:
        client = MongoDBClient()
        db = client.connect()
        coll = client.get_collection('guias')
        client.upsert('guias', {'subject': 'ABC'}, doc)
        client.close()
    """

    def __init__(self, uri: str | None = None, db_name: str | None = None):
        # Prefer an explicit MONGO_URI. If not provided, try to construct one from
        # compose-friendly variables (MONGO_HOSTNAME, MONGO_PORT, MONGO_ROOT_USERNAME,
        # MONGO_ROOT_PASSWORD, MONGO_AUTH_DB). Fall back to localhost if nothing is set.
        env_uri = os.getenv("MONGO_URI")
        if uri:
            self.uri = uri
        elif env_uri:
            self.uri = env_uri
        else:
            host = os.getenv("MONGO_HOSTNAME")
            port = os.getenv("MONGO_PORT")
            user = os.getenv("MONGO_ROOT_USERNAME")
            password = os.getenv("MONGO_ROOT_PASSWORD")
            auth_db = os.getenv("MONGO_AUTH_DB")

            if host:
                # Build credentials if provided
                if user and password:
                    # include authSource if provided
                    if auth_db:
                        self.uri = f"mongodb://{user}:{password}@{host}:{port or 27017}/?authSource={auth_db}"
                    else:
                        self.uri = f"mongodb://{user}:{password}@{host}:{port or 27017}"
                else:
                    self.uri = f"mongodb://{host}:{port or 27017}"
            else:
                # last resort: localhost
                self.uri = "mongodb://localhost:27017"
        self.db_name = db_name or os.getenv("MONGO_DB", "tfg_chatbot")
        self.client: MongoClient | None = None
        self.db = None

    def connect(self):
        """Connect to MongoDB and return the database object."""
        if self.client is None:
            # lazy connect
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
        return self.db

    def get_collection(self, name: str):
        if self.db is None:
            self.connect()
        if self.db is None:
            raise ValueError("Failed to connect to database")
        return self.db[name]

    def close(self):
        """Close the client connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

    def upsert(
        self, collection_name: str, filter_query: dict[str, Any], doc: dict[str, Any]
    ):
        """Replace the document matching filter_query or insert if not exists."""
        coll = self.get_collection(collection_name)
        result = coll.replace_one(filter_query, doc, upsert=True)
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None,
        }

    def find_by_subject(self, collection_name: str, subject: str):
        coll = self.get_collection(collection_name)
        return coll.find_one({"subject": subject})
