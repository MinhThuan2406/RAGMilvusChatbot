# RAGChatbot User Guide

Welcome! This guide helps you run and use RAGChatbot.

---

## Quick Start

- Install Docker & Docker Compose.
- Run:
  ```sh
  docker compose up --build
  ```
- Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Uploading Documents

- Put files in `data/raw_docs/`.
- Use the UI to upload or trigger ingestion.

---

## Remote Access

- Use Ngrok for remote access:
  ```sh
  ngrok http --region=ap 3000
  ```

---

## Need Help?

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common problems.
