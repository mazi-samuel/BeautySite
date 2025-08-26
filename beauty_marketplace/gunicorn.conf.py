# Gunicorn configuration file for BeautyMarket

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000

# Logging
accesslog = "/var/log/beautymarket/gunicorn_access.log"
errorlog = "/var/log/beautymarket/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "beautymarket"

# Server mechanics
daemon = False
pidfile = "/var/run/beautymarket.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Server hooks
def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")
