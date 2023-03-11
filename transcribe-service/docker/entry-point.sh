UPLOAD_FOLDER=/srv/data/files/
mkdir -p $UPLOAD_FOLDER

gunicorn --workers=2 --graceful-timeout 90 --timeout 90 transcribe-service:app -b 0.0.0.0:8700
