"""
MongoDB connection management with connection pooling.
Supports local MongoDB and AWS DocumentDB.
Gracefully handles connection failures by providing dummy objects.
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load env explicitly to ensure it's available when imported
load_dotenv()

class DummyCollection:
    """A dummy collection that swallows operations when DB is down."""
    def insert_one(self, *args, **kwargs): return None
    def insert_many(self, *args, **kwargs): return None
    def find(self, *args, **kwargs): return []
    def find_one(self, *args, **kwargs): return None
    def update_one(self, *args, **kwargs): return None
    def delete_one(self, *args, **kwargs): return None
    def count_documents(self, *args, **kwargs): return 0

class DummyDatabase:
    """A dummy database that returns dummy collections."""
    def __getitem__(self, name):
        return DummyCollection()

class MongoConnection:
    _instance = None
    _client = None
    db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._connect()

    def _connect(self):
        uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("MONGODB_DB", "vr_recommender")

        if not uri:
             print("⚠ Warning: MONGODB_URI not found in env, defaulting to localhost")
             uri = "mongodb://localhost:27017/"

        try:
            # Connection options for production
            self._client = MongoClient(
                uri,
                maxPoolSize=50,
                minPoolSize=10,
                serverSelectionTimeoutMS=3000, # Reduced timeout for faster failover
                connectTimeoutMS=3000
            )
            
            # Trigger a connection check
            self._client.admin.command('ismaster')
            
            self.db = self._client[db_name]
            print(f"✓ Connected to MongoDB: {db_name}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"⚠ MongoDB connection failed: {e}")
            print("⚠ Running in NO-DB mode. Chat logs will not be saved.")
            self.db = DummyDatabase()
            self._client = None
            
    def get_collection(self, name: str):
        if self.db is None:
            return DummyCollection()
        return self.db[name]

    def close(self):
        if self._client:
            self._client.close()

# Global instance
mongo = MongoConnection()