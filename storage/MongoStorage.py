# storage/MongoStorage.py
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from pymongo import MongoClient, ASCENDING, errors
import certifi
from .Storage import Storage
from config.Config import DATABASE_URI


class MongoStorage(Storage):
    def __init__(self, mongo_uri: Optional[str] = None, db_name: str = "scrapper_db"):
        self._mongo_uri = mongo_uri or DATABASE_URI
        self._db_name = db_name
        self._client: Optional[MongoClient] = None
        self._db = None
        self._posts = None
        self._connect()

    def _connect(self) -> None:
        """Establish MongoDB connection with basic health check."""
        try:
            self._client = MongoClient(
                self._mongo_uri,
                tls=True,                     # enables TLS/SSL
                tlsCAFile=certifi.where(),    # path to certifi's CA bundle
                serverSelectionTimeoutMS=5000
            )
            self._db = self._client[self._db_name]
            self._posts = self._db["posts"]

            # Verify connection
            self._client.admin.command("ping")

            # Ensure index on canonical_hash
            self._posts.create_index(
                [("canonical_hash", ASCENDING)], unique=True, background=True
            )

        except errors.ServerSelectionTimeoutError as e:
            raise RuntimeError(f"Could not connect to MongoDB: {e}")

    def upsert_post(self, doc: Dict[str, Any]) -> None:
        """Insert or update a post document based on canonical_hash."""
        if self._posts is None:
            raise RuntimeError("MongoDB collection not initialized.")

        if "canonical_hash" not in doc:
            raise ValueError("Document missing required field: canonical_hash")

        now = datetime.now(timezone.utc)
        
        # copy doc to avoid mutating caller's dict
        update_fields = {**doc, "updated_at": now}
        
        # If caller didn’t supply created_at, set it only on insert
        set_on_insert = {}
        if "created_at" not in doc:
            set_on_insert["created_at"] = now
            
        try:
            update_doc = {"$set": update_fields}
            if set_on_insert:
                update_doc["$setOnInsert"] = set_on_insert

            self._posts.update_one(
                {"canonical_hash": doc["canonical_hash"]},
                update_doc,
                upsert=True,
            )
        except errors.PyMongoError as e:
            raise RuntimeError(f"Mongo upsert failed: {e}")
