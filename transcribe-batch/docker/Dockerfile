FROM python:3.11.0-slim-bullseye as copied_files

COPY transcribe-batch/requirements.txt /srv/
COPY transcribe-batch/*.py /srv/
COPY transcribe-batch/docker/entry-point.sh /srv/

FROM python:3.11.0-slim-bullseye

RUN apt-get update -y && apt-get upgrade -y && apt-get install git -y
RUN apt-get install python3-pip -y --no-install-recommends
RUN pip3 install --upgrade pip && pip3 install --upgrade setuptools

COPY --from=copied_files /srv/ /srv/

WORKDIR /srv
RUN pip3 install -r requirements.txt

ENTRYPOINT /srv/entry-point.sh
#ENTRYPOINT bash
