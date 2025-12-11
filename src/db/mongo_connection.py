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

    def _connect(self):
        uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("MONGODB_DB", "vr_recommender")

        if not uri:
             print("⚠ Warning: MONGODB_URI not found in env, defaulting to localhost")
             uri = "mongodb://localhost:27017/"

        # Connection options for production
        self._client = MongoClient(
            uri,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=3000, # Reduced timeout for faster failover
            connectTimeoutMS=3000
        )
        
        # Trigger a connection check - This will RAISE an exception if it fails
        self._client.admin.command('ismaster')
        
        self.db = self._client[db_name]
        print(f"✓ Connected to MongoDB: {db_name}")
            
    def get_collection(self, name: str):
        if self.db is None:
            raise ConnectionFailure("MongoDB is not connected")
        return self.db[name]

    def close(self):
        if self._client:
            self._client.close()

# Global instance
mongo = MongoConnection()