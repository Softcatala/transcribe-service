UPLOAD_FOLDER=/srv/data/files/
mkdir -p $UPLOAD_FOLDER

# The requests do not requiere CPU since they are waiting from CTranslate2, then threads is more appropiated
gunicorn --workers=2 --graceful-timeout 90 --timeout 90 --threads=4 transcribe-service:app -b 0.0.0.0:8700
