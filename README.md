# VR Recommender System

An intelligent VR app recommendation system for CMU Heinz College that combines RAG (Retrieval-Augmented Generation), knowledge graphs, and vector search to provide personalized Meta Quest VR app recommendations based on student learning goals.

## 🚀 Quick Start (Recommended)

The project includes a robust all-in-one startup script that handles everything:

```bash
# Start all services (Neo4j + MongoDB + Flask API)
./start_project.sh
```

**What this script does:**
1.  **Checks Environment**: Ensures Python dependencies are installed.
2.  **Starts Databases**: Checks for and starts Neo4j and MongoDB services.
3.  **Cleans Ports**: Automatically frees up ports 5000/5001 if they are in use.
4.  **Launches App**: Starts the Flask API server.
5.  **Shows Logs**: Streams the application logs to your terminal.

### Other Startup Options

*   **Background Mode**: Run `./start_project.sh --background` to start services silently and detach.
*   **Force Restart**: Run `./start_project.sh --force` (or `./restart.sh`) to stop all running instances and restart fresh.
*   **Status Check**: Run `./status.sh` to view the health of all services.
*   **Stop**: Run `./stop_all.sh` to cleanly shut down all services.

### Access Points

*   **Chatbot Interface**: http://localhost:5000/
*   **API Health Check**: http://localhost:5000/health
*   **Neo4j Browser**: http://localhost:7474
*   **Admin Dashboard**: http://localhost:5000/admin (Login required)

## 🐳 Docker Deployment (Production)

For production deployment, use Docker Compose to run all services in containers.

### Prerequisites

-   Docker & Docker Compose installed
-   The `.env` file is already included in this repository with all required API keys and configurations

### Start with Docker Compose

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop all services
docker-compose -f docker-compose.prod.yml down
```

### Docker Services

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| **vr-recommender** | vr-recommender | 5001:5000 | Flask API with Gunicorn |
| **redis** | vr-redis | 6379:6379 | Rate limiting & caching |
| **neo4j** | vr-neo4j | 7474, 7687 | Knowledge graph database |

### Docker Access Points

*   **Chatbot Interface**: http://localhost:5001/
*   **API Health Check**: http://localhost:5001/health
*   **Neo4j Browser**: http://localhost:7474

### Docker Commands

```bash
# Rebuild after code changes
docker-compose -f docker-compose.prod.yml up -d --build vr-recommender

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f vr-recommender

# Check container health
docker ps

# Enter container shell
docker exec -it vr-recommender /bin/bash

# Remove volumes (reset data)
docker-compose -f docker-compose.prod.yml down -v
```

## 🏗 Architecture

The system uses a **RAG (Retrieval-Augmented Generation)** pipeline:

1.  **Query Understanding**: LLM (Gemini 2.0) analyzes user intent.
2.  **Vector Search (ChromaDB)**: Retrieves semantically similar skills/courses.
3.  **Knowledge Graph (Neo4j)**: Traverses relationships (`VRApp` -> `DEVELOPS` -> `Skill`).
    *   *New*: Includes "Semantic Bridge" logic to connect unrelated terms.
4.  **Ranking (LLM)**: Ranks candidates and generates transparent reasoning.

## 🛠 Key Tech Stack

-   **Language**: Python 3.9+
-   **Web Framework**: Flask, Gunicorn
-   **Databases**: Neo4j (Graph), ChromaDB (Vector), MongoDB (Data/Logs)
-   **LLM Provider**: OpenRouter (Gemini 2.0 Flash)
-   **Data Collection**: Firecrawl, Tavily

## ⚡ Scalability & Concurrency

The system supports **up to 16 concurrent requests** via Gunicorn's threaded worker model.

### Configuration

| Setting | Value | File |
|---------|-------|------|
| Workers | 4 | `web/gunicorn_config.py` |
| Threads/Worker | 4 | `web/gunicorn_config.py` |
| Max Concurrent Requests | 16 | (4 × 4) |
| Request Timeout | 120s | `web/gunicorn_config.py` |
| MongoDB Pool | 10-50 connections | `src/db/mongo_connection.py` |

### Rate Limits (per IP)

| Endpoint | Limit |
|----------|-------|
| `/chat` | 10/minute |
| `/api/auth/login` | 5/minute |
| Global | 200/day, 50/hour |

### Scaling Tips

-   Increase `workers` in `gunicorn_config.py` for higher traffic (recommended: 2× CPU cores)
-   Redis is used for distributed rate limiting across workers
-   MongoDB connection pool auto-scales up to 50 connections

## 📂 Project Structure

```
vr-recommender/
├── flask_api.py               # REST API server
├── vr_recommender.py          # Core RAG logic
├── start_project.sh           # Main entry point
├── requirements.txt           # Python dependencies
├── src/
│   ├── rag/                   # RAG System (Retriever, Ranker)
│   ├── chat/                  # Chat Session Management
│   ├── knowledge_graph/       # Neo4j Graph Builder
│   ├── vector_store/          # ChromaDB Vector Search
│   └── db/                    # MongoDB Repositories
├── data_collection/           # Data Scraping Scripts
└── scripts/                   # Maintenance Utilities
```

## 📝 Development Notes

-   **Environment Variables**: Stored in `.env` (Requires `OPENROUTER_API_KEY`, `NEO4J_URI`, etc.).
-   **Updating Data**: Use the Admin Dashboard (`/admin/data`) to trigger scrapers or rebuild graphs.
-   **Testing**: Run `pytest` or use the `./diagnose.sh` script for system checks.

## License

MIT License - see LICENSE file for details.