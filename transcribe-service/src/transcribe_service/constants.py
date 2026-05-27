import os

UPLOAD_FOLDER = "/srv/data/files/"

PROCESSED_FOLDER = "/srv/data/processed/"

LOGDIR = os.getenv("LOGDIR", "")

LOGLEVEL = os.getenv("LOGLEVEL", "INFO").upper()

ALLOWED_MIMEYPES = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "ogg": "application/ogg",
    "flac": "audio/flac",
    "avi": "video/x-msvideo",
    "mp4": "video/mp4",
    "mkv": "video/x-matroska",
    "mov": "video/quicktime",
    "mts": "video/mts",
}

QUEUE_CAPACITY = int(os.getenv("QUEUE_CAPACITY", "150"))

# 1GB by default
MAX_SIZE = int(os.getenv("MAX_SIZE", 1024 * 1024 * 1024))

MAX_PER_EMAIL = int(os.getenv("MAX_PER_EMAIL", "3"))
