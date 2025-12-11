#!/bin/bash
# VR Recommender - Ubuntu Deployment Script
# Automates the setup steps from DEPLOY.md

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 1. Check Prerequisites (Docker)
log_info "Checking Docker..."
if ! command -v docker &> /dev/null; then
    log_warn "Docker not found. Installing..."
    if [ "$EUID" -ne 0 ]; then
        log_error "Please run as root (sudo) to install Docker."
        exit 1
    fi
    apt-get update
    apt-get install -y docker.io docker-compose-v2
    systemctl enable --now docker
    log_info "Docker installed."
else
    log_info "Docker is already installed."
fi

# 2. Check Environment
if [ ! -f .env ]; then
    log_error ".env file not found!"
    echo "Please create a .env file with your API keys and configuration."
    echo "You can use the example in DEPLOY.md as a template."
    exit 1
fi

# 3. Launch Services
log_info "Building and starting services..."
# Ensure we use the production compose file
docker compose -f docker-compose.prod.yml up -d --build

log_info "Waiting for services to stabilize (10s)..."
sleep 10

# 4. Initialize Data
log_info "Waiting for Neo4j to be ready..."
MAX_RETRIES=30
COUNT=0
while [ $COUNT -lt $MAX_RETRIES ]; do
    if docker exec vr-recommender python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.connect(('neo4j', 7687)); s.close()" 2>/dev/null; then
        log_info "Neo4j is ready!"
        break
    fi
    log_warn "Neo4j not ready yet... retrying ($((COUNT+1))/$MAX_RETRIES)"
    sleep 2
    COUNT=$((COUNT+1))
done

if [ $COUNT -eq $MAX_RETRIES ]; then
    log_error "Timed out waiting for Neo4j."
    exit 1
fi

log_info "Initializing Knowledge Graph (Neo4j)..."
docker exec -it vr-recommender python scripts/build_graph.py

log_info "Initializing Vector Index (ChromaDB)..."
docker exec -it vr-recommender python vector_store/scripts/build_vector_index.py

# 4b. Restart Flask to reload DB connection
log_info "Restarting Flask API to load new data..."
docker restart vr-recommender
log_info "Waiting for API to restart (5s)..."
sleep 5

# 5. Final Check
log_info "Checking API health..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║             Deployment Successful! 🚀                            ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo "API is running at: http://localhost:8080"
else
    log_error "Health check failed. Check logs with: docker compose -f docker-compose.prod.yml logs"
fi
