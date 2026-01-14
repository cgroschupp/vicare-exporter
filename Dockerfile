FROM ghcr.io/astral-sh/uv:0.9.25-python3.12-alpine AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --no-editable

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

FROM python:3.12-alpine


COPY --from=builder /app/.venv /app/.venv

ENV PATH=/app/.venv/bin:$PATH

EXPOSE 9100

CMD [ "python", "-m", "vicare_exporter" ]
