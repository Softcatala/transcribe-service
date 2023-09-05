UPLOAD_FOLDER=/srv/data/files/
mkdir -p $UPLOAD_FOLDER

# High timeout to allow upload using POST of large video/audio files
gunicorn --workers=2 --graceful-timeout 600 --timeout 600 transcribe-service:app -b 0.0.0.0:8700
