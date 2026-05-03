FROM transcribe-models AS models

FROM nvidia/cuda:12.3.1-base-ubuntu22.04

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends ffmpeg sox libsox-fmt-mp3 libcudnn9-cuda-12 libcublas-12-3 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV UV_PYTHON_DOWNLOADS=automatic
ENV PATH="/workspace/.venv/bin:$PATH"

WORKDIR /workspace

COPY pyproject.toml uv.lock ./

COPY transcribe-core/pyproject.toml transcribe-core/

COPY transcribe-batch/pyproject.toml transcribe-batch/

RUN uv sync --frozen --package transcribe-batch --no-install-workspace

COPY transcribe-core/src transcribe-core/src

COPY transcribe-batch/src transcribe-batch/src

COPY transcribe-batch/email-templates transcribe-batch/email-templates

COPY transcribe-batch/audio transcribe-batch/audio

RUN uv sync --frozen --package transcribe-batch

COPY transcribe-batch/docker/entry-point.sh /srv/entry-point.sh

RUN chmod +x /srv/entry-point.sh

COPY --from=models /srv/models/ /root/.cache/huggingface/

WORKDIR /workspace/transcribe-batch

ENTRYPOINT ["/srv/entry-point.sh"]
