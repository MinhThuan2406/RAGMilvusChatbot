# RAGChatbot Troubleshooting Guide

Common issues and solutions.

---

## Service Not Starting

- Check logs:
  ```sh
  docker compose logs -f
  ```
- Make sure ports 8000, 8001, 11434, 3000 are free.
- Check your `.env` file.

---

## CORS Errors

- Ensure `CORS_ALLOW_ORIGIN` in `.env` matches your frontend URL.
- Restart backend after changes.

---

## Ngrok Not Working

- Check your Ngrok authtoken in `.env`.
- Check firewall.
- Use correct port.

---

## Ollama/Milvus Issues

- Make sure containers are running.
- Check logs for errors.
- Try:
  ```sh
  docker compose down -v
  docker compose up --build
  ```

---

## UI Not Loading

- Check frontend container.
- Try rebuilding:
  ```sh
  docker compose up --build
  ```
- Clear browser cache.

---

## More Help

- See [README.Docker.md](README.Docker.md) and [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md).
