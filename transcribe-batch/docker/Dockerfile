FROM python:3.11.1-slim-bullseye as copied_files

COPY transcribe-batch/*.py /srv/
COPY transcribe-batch/docker/entry-point.sh /srv/
COPY transcribe-batch/requirements.txt /srv/

FROM transcribe-models as models
FROM python:3.11.1-slim-bullseye

RUN apt-get update -y && apt-get upgrade -y && apt-get install ffmpeg sox libsox-fmt-mp3 -y

WORKDIR /srv

COPY --from=copied_files /srv/ /srv/
RUN pip3 install -r /srv/requirements.txt

COPY --from=models /srv/models/ /root/.cache/huggingface/

ENTRYPOINT /srv/entry-point.sh

