"""
Gunicorn production configuration for SPIDER
"""
import multiprocessing

# ─── Server Socket ───────────────────────────────────────
bind = "0.0.0.0:5000"
backlog = 2048

# ─── Workers ─────────────────────────────────────────────
# For SocketIO, use only 1 worker with threading
# (SocketIO sessions are not shared across workers without Redis)
workers = 1
worker_class = "gthread"
threads = multiprocessing.cpu_count() * 2 + 1
worker_connections = 1000
timeout = 120
keepalive = 5

# ─── Process Naming ──────────────────────────────────────
proc_name = "spider"

# ─── Logging ─────────────────────────────────────────────
accesslog = "/var/log/spider/access.log"
errorlog  = "/var/log/spider/error.log"
loglevel  = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ─── SSL (if not using Nginx as SSL terminator) ──────────
# keyfile  = "/etc/ssl/private/spider.key"
# certfile = "/etc/ssl/certs/spider.crt"

# ─── Process Management ──────────────────────────────────
preload_app = True
daemon = False

# ─── Hooks ───────────────────────────────────────────────
def on_starting(server):
    print("[SPIDER] Gunicorn master starting...")

def post_fork(server, worker):
    """Reset DB connection pool in each worker after forking.
    Without this, workers inherit the master's connections and
    get 'connection already closed' / psycopg2 errors.
    """
    try:
        from modules.database import db
        db.engine.dispose()
        print(f"[SPIDER] Worker {worker.pid} — DB pool reset")
    except Exception as e:
        print(f"[SPIDER] Worker {worker.pid} — pool reset warning: {e}")

def worker_exit(server, worker):
    print(f"[SPIDER] Worker {worker.pid} exiting")

def worker_abort(worker):
    print(f"[SPIDER] Worker {worker.pid} aborted — check logs")
