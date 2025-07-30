# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.9
FROM python:3.11.9-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    antiword \
    poppler-utils \
    tesseract-ocr \
    catdoc \
    unrtf \
    libxml2 \
    libxslt1.1 \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libopenjp2-7 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    gcc \
    build-essential \
    python3-dev \
    curl \
    wget \
    libtesseract-dev \
    libxml2-utils \
    imagemagick \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip==24.0

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --force-reinstall --upgrade six

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY . .

RUN mkdir -p /app/backend/data/vector_db && \
    chown -R appuser:appuser /app/backend/data/
RUN mkdir -p /app/.cache /app/data /app/.local && \
    chown -R appuser:appuser /app/.cache /app/data /app/.local

ENV USER_AGENT="RAGChatbot/1.0"
ENV MILVUS_TELEMETRY_ENABLED="false"

USER appuser

EXPOSE 8001

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "debug"]
