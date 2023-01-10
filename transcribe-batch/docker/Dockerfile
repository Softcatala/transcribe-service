FROM python:3.11.0-slim-bullseye as copied_files

RUN apt-get update -y && apt-get upgrade -y && apt-get install git ffmpeg make g++ -y

# Build Whisper.cpp
RUN git clone https://github.com/ggerganov/whisper.cpp
WORKDIR whisper.cpp
RUN git checkout 1.0.4 -q
RUN make
RUN mkdir -p /srv/whisper.cpp/
RUN cp main /srv/whisper.cpp/

COPY transcribe-batch/*.py /srv/
COPY transcribe-batch/docker/entry-point.sh /srv/

FROM transcribe-models as models
FROM python:3.11.0-slim-bullseye

RUN apt-get update -y && apt-get upgrade -y && apt-get install ffmpeg -y

WORKDIR /srv

COPY --from=copied_files /srv/ /srv/
COPY --from=models /models/ /srv/whisper.cpp/

#ENTRYPOINT bash
ENTRYPOINT /srv/entry-point.sh

