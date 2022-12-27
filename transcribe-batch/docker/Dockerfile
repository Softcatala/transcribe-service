FROM python:3.11.0-slim-bullseye as copied_files

COPY transcribe-batch/*.py /srv/
COPY transcribe-batch/docker/entry-point.sh /srv/

FROM python:3.11.0-slim-bullseye

RUN apt-get update -y && apt-get upgrade -y && apt-get install git ffmpeg -y
RUN apt-get install python3-pip -y --no-install-recommends
RUN pip3 install --upgrade pip && pip3 install --upgrade setuptools

WORKDIR /srv
COPY transcribe-batch/requirements.txt /srv/
RUN pip3 install -r requirements.txt

COPY --from=copied_files /srv/ /srv/
 # Modified versions with SC models
COPY transcribe-batch/whisper/__init__.py  /usr/local/lib/python3.11/site-packages/whisper/


ENTRYPOINT /srv/entry-point.sh
#ENTRYPOINT bash
