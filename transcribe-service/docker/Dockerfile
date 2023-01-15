FROM python:3.11.1-slim-bullseye as copied_files

COPY transcribe-service/*.py /srv/
COPY transcribe-service/docker/entry-point.sh /srv/


FROM python:3.11.1-slim-bullseye

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install python3-pip -y --no-install-recommends
RUN pip3 install --upgrade pip && pip3 install --upgrade setuptools

COPY transcribe-service/requirements.txt /srv/
WORKDIR /srv
RUN pip3 install -r requirements.txt

COPY --from=copied_files /srv/ /srv/

EXPOSE 8700

ENTRYPOINT /srv/entry-point.sh

