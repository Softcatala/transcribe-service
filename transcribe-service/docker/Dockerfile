FROM python:3.13.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /workspace

COPY pyproject.toml uv.lock ./

COPY transcribe-core/pyproject.toml transcribe-core/

COPY transcribe-service/pyproject.toml transcribe-service/

RUN uv sync --frozen --package transcribe-service --no-install-workspace

COPY transcribe-core/src transcribe-core/src

COPY transcribe-service/src transcribe-service/src

RUN uv sync --frozen --package transcribe-service

COPY transcribe-service/docker/entry-point.sh /srv/entry-point.sh

RUN chmod +x /srv/entry-point.sh

EXPOSE 8700

ENTRYPOINT ["/srv/entry-point.sh"]
