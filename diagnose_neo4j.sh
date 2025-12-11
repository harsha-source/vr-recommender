#!/bin/bash
# Neo4j Diagnostic Script for Ubuntu

echo "🔍 Starting Neo4j Diagnostics..."
echo "================================="

# 1. Check Container Status
echo "1. Checking Container Status..."
if docker ps | grep -q vr-neo4j; then
    echo "✅ Neo4j container is RUNNING"
else
    echo "❌ Neo4j container is NOT RUNNING"
    echo "   Last 10 lines of logs:"
    docker logs --tail 10 vr-neo4j 2>&1
    exit 1
fi

# 2. Check Ports
echo -e "\n2. Checking Ports..."
if netstat -tuln | grep -q 7687; then
    echo "✅ Port 7687 is listening"
else
    echo "❌ Port 7687 is NOT listening"
fi

# 3. Check Logs for Common Errors
echo -e "\n3. Checking Logs for Errors..."
LOGS=$(docker logs vr-neo4j 2>&1)

if echo "$LOGS" | grep -q "Permission denied"; then
    echo "❌ FOUND PERMISSION ERROR: 'Permission denied'"
    echo "   Fix: You might need to adjust volume permissions."
    echo "   Try: sudo chown -R 7474:7474 neo4j_data"
elif echo "$LOGS" | grep -q "OutOfMemory"; then
    echo "❌ FOUND MEMORY ERROR: 'OutOfMemory'"
    echo "   Fix: Increase server memory or add swap."
elif echo "$LOGS" | grep -q "Started"; then
    echo "✅ Neo4j seems to have started successfully."
else
    echo "⚠️ No obvious errors found, but check full logs."
fi

# 4. Test Internal Connection & Data
echo -e "\n4. Testing Internal Connection & Data..."

# Check if data files exist
echo "   Checking source data files..."
if docker exec vr-recommender ls -l data_collection/data/courses.json >/dev/null 2>&1; then
    echo "   ✅ courses.json found"
else
    echo "   ❌ courses.json NOT FOUND in container"
    echo "      (Did you git push the data? Or run data collection?)"
fi

# Check Neo4j Node Counts
echo "   Checking Neo4j Node Counts..."
docker exec vr-recommender python -c "
import os
from neo4j import GraphDatabase
uri = os.getenv('NEO4J_URI', 'bolt://neo4j:7687')
auth = (os.getenv('NEO4J_USER', 'neo4j'), os.getenv('NEO4J_PASSWORD', 'password'))
try:
    with GraphDatabase.driver(uri, auth=auth) as driver:
        with driver.session() as session:
            count = session.run('MATCH (n) RETURN count(n) as c').single()['c']
            print(f'   📊 Total Nodes in DB: {count}')
            if count == 0:
                print('   ⚠️  Database is EMPTY! Run ./deploy_ubuntu.sh again or check build logs.')
except Exception as e:
    print(f'   ❌ Connection Failed: {e}')
"

echo -e "\n================================="
echo "Diagnostics Complete."
