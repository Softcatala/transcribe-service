FROM python:3.11.1-slim-bullseye as copied_files

COPY transcribe-batch/*.py /srv/
COPY transcribe-batch/email-templates/ /srv/email-templates/
COPY transcribe-batch/docker/entry-point.sh /srv/
COPY transcribe-batch/requirements.txt /srv/
COPY transcribe-batch/audio/test_audio.mp3 /srv/audio/
COPY transcribe-batch/ctranslate2-4.6.1-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl /srv

FROM transcribe-models as models
FROM nvidia/cuda:12.3.1-base-ubuntu22.04

RUN apt-get update -y && apt-get upgrade -y && apt-get install ffmpeg sox libsox-fmt-mp3 -y
RUN apt-get install python3-pip python3-dev -y --no-install-recommends

# Solve errors:
# - Error: Unable to load any of {libcudnn_ops.so.9.1.0, libcudnn_ops.so.9.1, libcudnn_ops.so.9, libcudnn_ops.so}
# - Error: RuntimeError: Library libcublas.so.12 is not found or cannot be loaded

RUN apt-get install libcudnn9-cuda-12 libcublas-12-3 -y

WORKDIR /srv

COPY --from=copied_files /srv/ /srv/
RUN pip3 install ctranslate2-4.6.1-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
RUN pip3 install -r /srv/requirements.txt

COPY --from=models /srv/models/ /root/.cache/huggingface/

ENTRYPOINT /srv/entry-point.sh

