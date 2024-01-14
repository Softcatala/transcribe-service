UPLOAD_FOLDER=/srv/data/files/
mkdir -p $UPLOAD_FOLDER
# Notes on the configuration:
# - POST of large video/audio files can take over 1m depending on connection quality and file size
# - When you reproduce the media file from OTranscribe, it goes long requests to /get_file/, it can take
#   over 10 minutes
# - Timeout is applied per worker. This means that if a worker with a single thread (the default configuration)
#   takes more than the timeout, the worker will be restarted
gunicorn --workers=2 --threads=4 --graceful-timeout 600 --timeout 600 transcribe-service:app -b 0.0.0.0:8700
