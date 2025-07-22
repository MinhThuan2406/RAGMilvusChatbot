# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.13.2
# ARG PYTHON_VERSION=3.12
# ARG PYTHON_VERSION=3.11.4
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# ENV PYTHONPATH=/app/backend

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install system dependencies for document/image processing
RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    unrtf \
    antiword \
    catdoc \
    libxml2-utils \
    imagemagick \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# # Install Python dependencies as root
# RUN python -m pip install --upgrade pip==24.0
# RUN --mount=type=cache,target=/root/.cache/pip \
#     --mount=type=bind,source=requirements.txt,target=requirements.txt \
#     python -m pip install -r requirements.txt
RUN python -m pip install --upgrade pip==24.0
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# For debugging
RUN pip install --force-reinstall --upgrade six

# Copy source code as root
COPY . .

# Create and set permissions for all writable folders
RUN mkdir -p /app/.cache /app/data /app/.local && \
    chown -R appuser:appuser /app/.cache /app/data /app/.local

ENV USER_AGENT="RAGChatbot/1.0"
ENV MILVUS_TELEMETRY_ENABLED="false"

# Switch to non-root user
USER appuser

# Expose the port that the application listens on.
EXPOSE 8001

# Run the application with Uvicorn (FastAPI production server)
# CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "debug"]
# For debugging
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "debug"]