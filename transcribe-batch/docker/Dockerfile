FROM python:3.11.1-slim-bullseye as copied_files

COPY transcribe-batch/*.py /srv/
COPY transcribe-batch/email-templates/ /srv/email-templates/
COPY transcribe-batch/docker/entry-point.sh /srv/
COPY transcribe-batch/requirements.txt /srv/

FROM transcribe-models as models
FROM nvidia/cuda:12.3.1-base-ubuntu22.04

RUN apt-get update -y && apt-get upgrade -y && apt-get install ffmpeg sox libsox-fmt-mp3 -y
RUN apt-get install python3-pip python3-dev -y --no-install-recommends

# Solve errors:
# - Error: libcudnn_ops_infer.so.8: cannot open shared object file: No such file or directory
# - Error: libcublasLt.so.11: cannot open shared object file: No such file or directory
RUN apt-get install libcudnn8=8.8.1.3-1+cuda11.8 && apt-get install libcublas-12-3 &&  apt-get install libcublas-11-8 -y

WORKDIR /srv

COPY --from=copied_files /srv/ /srv/
RUN pip3 install -r /srv/requirements.txt

COPY --from=models /srv/models/ /root/.cache/huggingface/

ENTRYPOINT /srv/entry-point.sh

