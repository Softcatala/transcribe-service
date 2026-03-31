#!/usr/bin/env python3
import time
import os
import psutil

LOGDIR = os.environ.get("LOGDIR", "/tmp")
FILE = os.path.join(LOGDIR, "batch_metrics.txt")


def write_metrics(jobs_started=0, jobs_completed=0, files_processed=0, conversion_errors=0, whisper_not_catalan=0, whisper_timeout=0, files_stored=0, files_stored_mb=0, free_disk_mb=0, queue_size=0):
    """Write simple metrics to file"""
    try:
        uptime = time.time() - getattr(write_metrics, "_start", time.time())
        mem = psutil.Process().memory_info().rss / 1024 / 1024
        content = f"""# HELP batch_queue_size Current number of files in the queue
# TYPE batch_queue_size gauge
batch_queue_size {queue_size}
# HELP batch_jobs_started_total Total jobs started
# TYPE batch_jobs_started_total counter
batch_jobs_started_total {jobs_started}
# HELP batch_jobs_completed_total Total jobs completed
# TYPE batch_jobs_completed_total counter
batch_jobs_completed_total {jobs_completed}
# HELP batch_files_processed_total Total files processed
# TYPE batch_files_processed_total counter
batch_files_processed_total {files_processed}
# HELP batch_conversion_errors_total Total conversion errors
# TYPE batch_conversion_errors_total counter
batch_conversion_errors_total {conversion_errors}
# HELP batch_whisper_not_catalan_total Total files rejected as non-Catalan
# TYPE batch_whisper_not_catalan_total counter
batch_whisper_not_catalan_total {whisper_not_catalan}
# HELP batch_whisper_timeout_total Total files that timed out during transcription
# TYPE batch_whisper_timeout_total counter
batch_whisper_timeout_total {whisper_timeout}
# HELP batch_files_stored Current number of files stored
# TYPE batch_files_stored gauge
batch_files_stored {files_stored}
# HELP batch_files_stored_mb Disk space used by stored files in MB
# TYPE batch_files_stored_mb gauge
batch_files_stored_mb {files_stored_mb:.1f}
# HELP batch_free_disk_mb Free disk space in MB
# TYPE batch_free_disk_mb gauge
batch_free_disk_mb {free_disk_mb:.1f}
# HELP batch_uptime_seconds Uptime in seconds
# TYPE batch_uptime_seconds gauge
batch_uptime_seconds {uptime:.0f}
# HELP batch_memory_mb Memory usage in MB
# TYPE batch_memory_mb gauge
batch_memory_mb {mem:.1f}
"""
        open(FILE, "w").write(content)
    except:
        pass


write_metrics._start = time.time()
