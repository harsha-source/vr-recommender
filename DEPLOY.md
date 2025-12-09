# Deployment Guide for VR Recommender System (Ubuntu)

This guide provides step-by-step instructions to deploy the VR Recommender System on a fresh Ubuntu server using Docker. This is the most robust method as it isolates dependencies and ensures consistency.

## 1. Prerequisites

Update your system and install Docker and Docker Compose.

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
sudo apt install -y docker.io docker-compose-v2

# Start and enable Docker service
sudo systemctl enable --now docker

# Add your user to the docker group (avoids using sudo for docker commands)
sudo usermod -aG docker $USER
```

> [!IMPORTANT]
> After running the `usermod` command, you must **log out and log back in** for the changes to take effect.

## 2. Project Setup

### Clone the Repository
Upload your project files to the server or clone via Git.
```bash
# Example if using git
git clone <your-repo-url>
cd vr-recommender
```

### Configure Environment Variables
Create a `.env` file in the project root. This file contains sensitive keys and configuration.

```bash
nano .env
```

Paste the following configuration (adjust values as needed):

```ini
# API Keys (Required)
OPENROUTER_API_KEY=your_openrouter_key_here
FIRECRAWL_API_KEY=your_firecrawl_key_here
TAVILY_API_KEY=your_tavily_key_here

# Neo4j Configuration (Docker defaults)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Model Configuration
OPENROUTER_MODEL=google/gemini-2.0-flash-001

# Security
ADMIN_PASSWORD=HeinzVR2025!
FLASK_SECRET_KEY=generate_a_secure_random_string

# MongoDB (Optional - for logs)
# If using a remote cluster:
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?appName=app
MONGODB_DB=vr_recommender
```

## 3. Launch the Application

Use Docker Compose to build and start the services (Flask API, Neo4j, Redis).

```bash
# Build and start in detached mode (background)
docker compose -f docker-compose.prod.yml up -d --build
```

Check the status of the containers:
```bash
docker compose -f docker-compose.prod.yml ps
```
You should see `vr-recommender`, `vr-neo4j`, and `vr-redis` running.

## 4. Initialize Data

Once the containers are running, you need to populate the databases. Run these commands to execute the build scripts *inside* the application container.

### Build Knowledge Graph (Neo4j)
```bash
docker exec -it vr-recommender python scripts/build_graph.py
```

### Build Vector Index (ChromaDB)
```bash
docker exec -it vr-recommender python vector_store/scripts/build_vector_index.py
```

## 5. Verification

Test that the API is responding.

```bash
curl http://localhost:5001/health
```
You should receive a `200 OK` response.

## 6. Maintenance

- **View Logs**:
  ```bash
  docker compose -f docker-compose.prod.yml logs -f
  ```
- **Stop Application**:
  ```bash
  docker compose -f docker-compose.prod.yml down
  ```
- **Update Application**:
  1. `git pull` (or upload new files)
  2. `docker compose -f docker-compose.prod.yml up -d --build`
