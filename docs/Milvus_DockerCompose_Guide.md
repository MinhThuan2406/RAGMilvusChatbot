# Milvus Setup Guide with Docker Compose

This guide explains how to start Milvus as a vector database for RAGChatbot using Docker Compose.

---

## Prerequisites
- [Docker](https://www.docker.com/) installed
- [Docker Compose](https://docs.docker.com/compose/) installed

---

## 1. Environment Variables

Create a `.env` file in your project root (if not present) and add:

```env
MILVUS_HOST=milvus-db
MILVUS_PORT=19530
```

You can adjust these values as needed for your environment.

---

## 2. Docker Compose Service

Add the following service to your `compose.yml`:

```yaml
db-milvus:
  image: milvusdb/milvus:v2.3.9
  container_name: milvus-db
  ports:
    - "${MILVUS_PORT:-19530}:19530"
  environment:
    - MILVUS_PORT=${MILVUS_PORT:-19530}
  volumes:
    - milvus-data:/var/lib/milvus
  restart: unless-stopped
```

Or use the existing `milvus-db` service in your `compose.yml`.

---

## 3. Start All Services

From your project root, run:

```sh
docker compose up --build
```

This will start Milvus, Ollama, backend, and UI containers.

---

## 4. Verify Milvus Connection

Check that Milvus is running:

- Milvus should be accessible at `localhost:19530` (or your configured port).
- You can check logs with:

```sh
docker compose logs milvus-db
```

---

## 5. Troubleshooting
- If Milvus does not start, check Docker logs and port conflicts.
- See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for more help.

---

## References
- [Milvus Documentation](https://milvus.io/docs)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---

**RAGChatbot Team**
