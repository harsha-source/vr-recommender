#!/bin/bash
# Comprehensive Database Check Script
# Checks: Neo4j, ChromaDB, Redis, and MongoDB

echo "🔍 Starting Database Health Check..."
echo "==================================="

# Helper to run python code inside container
run_py() {
    docker exec vr-recommender python -c "$1" 2>/dev/null
}

# 1. Neo4j Check
echo -e "\n1. 🕸️  Checking Neo4j (Graph DB)..."
docker exec vr-recommender python -c "
import os
from neo4j import GraphDatabase
uri = os.getenv('NEO4J_URI', 'bolt://neo4j:7687')
auth = (os.getenv('NEO4J_USER', 'neo4j'), os.getenv('NEO4J_PASSWORD', 'password'))
try:
    with GraphDatabase.driver(uri, auth=auth) as driver:
        with driver.session() as session:
            count = session.run('MATCH (n) RETURN count(n) as c').single()['c']
            print(f'   ✅ Connected! Total Nodes: {count}')
            if count == 0: print('   ⚠️  Warning: Graph is empty.')
except Exception as e:
    print(f'   ❌ Connection Failed: {e}')
"

# 2. ChromaDB Check
echo -e "\n2. 🌈 Checking ChromaDB (Vector Store)..."
docker exec vr-recommender python -c "
import os
import chromadb
try:
    # Path inside container
    persist_dir = 'vector_store/data/chroma'
    client = chromadb.PersistentClient(path=persist_dir)
    col = client.get_or_create_collection('skills')
    count = col.count()
    print(f'   ✅ Connected! Total Vectors: {count}')
    if count == 0: print('   ⚠️  Warning: Vector index is empty.')
except Exception as e:
    print(f'   ❌ Check Failed: {e}')
"

# 3. Redis Check
echo -e "\n3. ⚡ Checking Redis (Cache)..."
docker exec vr-recommender python -c "
import os
import redis
try:
    r = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))
    if r.ping():
        print('   ✅ Connected! Redis is responding.')
        print(f'   📊 Keys in cache: {len(r.keys())}')
except Exception as e:
    print(f'   ❌ Connection Failed: {e}')
"

# 4. MongoDB Check
echo -e "\n4. 🍃 Checking MongoDB (Logs)..."
docker exec vr-recommender python -c "
import os
from pymongo import MongoClient
try:
    uri = os.getenv('MONGODB_URI')
    if not uri:
        print('   ℹ️  Skipped (MONGODB_URI not set)')
    else:
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        client.admin.command('ismaster')
        db = client[os.getenv('MONGODB_DB', 'vr_recommender')]
        count = db.interactions.count_documents({})
        print(f'   ✅ Connected! Total Interaction Logs: {count}')
except Exception as e:
    print(f'   ❌ Connection Failed: {e}')
"

echo -e "\n==================================="
echo "Check Complete."
