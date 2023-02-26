FROM python:3.11.1-slim-bullseye as copied_files

RUN apt-get update -y && apt-get upgrade -y && apt-get install git ffmpeg make g++ -y

COPY Makefile .
RUN make whisper.cpp
RUN mkdir -p /srv/whisper.cpp/
RUN cp whisper.cpp/main /srv/whisper.cpp/

COPY transcribe-batch/*.py /srv/
COPY transcribe-batch/docker/entry-point.sh /srv/

FROM transcribe-models as models
FROM python:3.11.1-slim-bullseye

RUN apt-get update -y && apt-get upgrade -y && apt-get install ffmpeg sox libsox-fmt-mp3 -y

WORKDIR /srv

COPY --from=copied_files /srv/ /srv/
COPY --from=models /srv/whisper.cpp/sc-models/ /srv/whisper.cpp/sc-models/

ENTRYPOINT /srv/entry-point.sh

