import multiprocessing
import os

# Gunicorn Configuration

# Bind to all interfaces on port 5001 (To avoid conflict with AirPlay on 5000)
bind = "0.0.0.0:5000"

# Worker configuration
# IMPORTANT: Must use workers=1 to maintain job state consistency.
# The JobManager stores job state in memory, so multiple workers would each
# have their own state and status polling would fail.
# Use threads for concurrency instead of multiple workers.
workers = 1
threads = 8  # Increased threads to compensate for single worker
worker_class = "gthread" # Use threaded workers

# Timeouts
# LLMs can be slow, so we need a generous timeout
timeout = 120 
keepalive = 5

# Logging
accesslog = "-" # Stdout
errorlog = "-"  # Stderr
loglevel = "info"

# Development reload (turn off in production usually, but useful for now)
reload = False

# App module
wsgi_app = "flask_api:app"

# Environment
raw_env = [
    "FLASK_ENV=production"
]