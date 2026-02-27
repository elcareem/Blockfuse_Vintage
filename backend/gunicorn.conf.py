"""
Gunicorn configuration file for production deployment.

Worker formula: (2 * CPU cores) + 1
"""
import multiprocessing
import os

# ─── Server socket ───────────────────────────────────────────────────────────
bind = "0.0.0.0:8000"
backlog = 2048

# ─── Workers ─────────────────────────────────────────────────────────────────
workers = (2 * multiprocessing.cpu_count()) + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
threads = 1

# ─── Timeouts ────────────────────────────────────────────────────────────────
timeout = 120              # kill workers silent for >120s
keepalive = 5             # keep idle connections open for 5s
graceful_timeout = 30     # allow workers 30s to finish requests on shutdown

# ─── Logging ─────────────────────────────────────────────────────────────────
accesslog = "-"           # stdout
errorlog = "-"            # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ─── Process naming ──────────────────────────────────────────────────────────
proc_name = "blockfuse_vintage"

# ─── Security ────────────────────────────────────────────────────────────────
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# ─── Environment ─────────────────────────────────────────────────────────────
# No debug mode in production
reload = False
preload_app = True   # load app before forking workers (saves memory via copy-on-write)
