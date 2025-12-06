from pymongo import MongoClient

from backend.config import settings


class MongoDBClient:
    """Simple MongoDB helper to connect, get collections and perform common ops."""

    def __init__(self, uri: str | None = None, db_name: str | None = None):
        # Use provided URI, or get from settings (which handles all the logic)
        if uri:
            self.uri = uri
        else:
            self.uri = settings.get_mongo_uri()

        self.db_name = db_name or settings.db_name
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
