#!/bin/sh

UPLOAD_FOLDER=/srv/data/files/
mkdir -p $UPLOAD_FOLDER
# Notes on the configuration:
# - POST of large video/audio files can take over 1m depending on connection quality and file size
# - When you reproduce the media file from OTranscribe, it goes long requests to /get_file/, it can take
#   over 10 minutes
# - Timeout is applied per worker. This means that if a worker with a single thread (the default configuration)
#   takes more than the timeout, the worker will be restarted
uv run --no-sync uvicorn transcribe_service.main:app --host 0.0.0.0 --port 8700
