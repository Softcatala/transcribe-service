#!/usr/bin/env python3
import time
import os
import psutil

LOGDIR = os.environ.get("LOGDIR", "/tmp")
FILE = os.path.join(LOGDIR, "batch_metrics.txt")

def write_metrics(jobs_started=0, jobs_completed=0, files_processed=0):
    """Write simple metrics to file"""
    try:
        uptime = time.time() - getattr(write_metrics, '_start', time.time())
        mem = psutil.Process().memory_info().rss / 1024 / 1024
        content = f"""# HELP batch_jobs_started_total Total jobs started
# TYPE batch_jobs_started_total counter
batch_jobs_started_total {jobs_started}
# HELP batch_jobs_completed_total Total jobs completed
# TYPE batch_jobs_completed_total counter
batch_jobs_completed_total {jobs_completed}
# HELP batch_files_processed_total Total files processed
# TYPE batch_files_processed_total counter
batch_files_processed_total {files_processed}
# HELP batch_uptime_seconds Uptime in seconds
# TYPE batch_uptime_seconds gauge
batch_uptime_seconds {uptime:.0f}
# HELP batch_memory_mb Memory usage in MB
# TYPE batch_memory_mb gauge
batch_memory_mb {mem:.1f}
"""
        open(FILE, 'w').write(content)
    except: pass

write_metrics._start = time.time()
