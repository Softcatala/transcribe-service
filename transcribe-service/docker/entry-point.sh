UPLOAD_FOLDER=/srv/data/files/
mkdir -p $UPLOAD_FOLDER

gunicorn --workers=4 --graceful-timeout 300 --timeout 300 transcribe-service:app -b 0.0.0.0:8700
