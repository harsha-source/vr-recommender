Stage 23: Docker Configuration Update for Agent Module

     Overview

     Verify and optimize Docker configuration after adding the src/agent/ module in Stage 22.

     Current Status

     Good News: Docker 配置大部分已正确：
     - Dockerfile.prod: COPY . . 已包含 src/agent/
     - requirements.txt: 所有依赖已存在
     - docker-compose.prod.yml: 服务配置正确

     唯一问题: 缺少 .dockerignore 文件

     Implementation Plan

     Step 1: Create .dockerignore

     # Python cache
     __pycache__/
     *.pyc
     *.pyo
     .pytest_cache/

     # Virtual environments
     venv/
     .venv/

     # IDE
     .idea/
     .vscode/
     *.swp
     .DS_Store

     # Git
     .git/
     .github/

     # Development files
     stage-dev/
     outdated/
     logs/
     .claude/
     .playwright-mcp/

     Step 2: Rebuild Docker Image

     docker-compose -f docker-compose.prod.yml up -d --build vr-recommender

     Step 3: Verify Agent Works

     # Check logs for "✓ Conversation Agent ready!"
     docker logs vr-recommender --tail 20

     # Test greeting
     printf '{"message": "hi there"}' | curl -s -X POST http://localhost:5001/chat -H "Content-Type: 
     application/json" -d @-

     # Test search
     printf '{"message": "find VR apps for data science"}' | curl -s -X POST http://localhost:5001/chat -H 
     "Content-Type: application/json" -d @-

     Step 4: Document

     Create stage-dev/stage-23-docker-update.md

     Files to Create

     | File                                | Action |
     |-------------------------------------|--------|
     | .dockerignore                       | CREATE |
     | stage-dev/stage-23-docker-update.md | CREATE |

     Verification Checklist

     - .dockerignore created
     - Docker image rebuilt
     - Agent logs show ready
     - Greeting test passes
     - Search test passes