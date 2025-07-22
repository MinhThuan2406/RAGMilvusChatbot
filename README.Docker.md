
# RAGChatbot Docker & Deployment Guide

---

## 🚀 Quick Start

See [USER_GUIDE.md](USER_GUIDE.md) for how to use the chatbot.
See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for development and API details.

To start all services:
```sh
docker compose up --build
```

Service URLs:
- Backend API: [http://localhost:8001](http://localhost:8001)
- ChromaDB: [http://localhost:8000](http://localhost:8000)
- Ollama: [http://localhost:11434](http://localhost:11434)
- Web UI: [http://localhost:3000](http://localhost:3000)

---

## 🛠️ Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Ngrok](https://ngrok.com/) (optional, for remote access)

---

## 📝 Environment Variables

All main configuration is handled via the `.env` file in the project root. Example variables:

```env
CHROMA_HOST=vector-db
CHROMA_PORT=8000
OLLAMA_HOST=ollama-llm
OLLAMA_PORT=11434
RAG_API_PORT=8001
CHATBOT_UI_PORT=3000
OPENAI_API_KEY=your-key
NGROK_AUTHTOKEN=your-ngrok-token
CORS_ALLOW_ORIGIN=http://localhost:3000
CORS_ALLOW_ORIGIN=https://your-production-domain.com
```

---

## 🩺 Service Health & Logs

- Check running containers:
  ```sh
  docker compose ps
  ```
- View logs for all services:
  ```sh
  docker compose logs -f
  ```

---

## 🌐 Expose Your Project Publicly with Ngrok

You can use [Ngrok](https://ngrok.com/) to share your local services for quick demos or remote access.


**Expose the FastAPI backend:**
1. [Download Ngrok](https://ngrok.com/download) and install it.
2. Start your stack as above.
3. In a new terminal, run:
   ```sh
   ngrok http --region=ap 8001
   ```
   Ngrok will provide a public URL forwarding to your FastAPI backend.

   > **Tip:** For best performance in Vietnam or Asia, always use the Asia Pacific region by adding `--region=ap` to your ngrok command, or set this in your `.env` file:
   >
   > ```env
   > NGROK_REGION=ap
   > ```
   >
   > This ensures ngrok tunnels are created in the Asia Pacific region for lower latency.

**Expose other ports:**
   - For the UI: `ngrok http --region=ap 3000`
   - For ChromaDB: `ngrok http --region=ap 8000`

**Security note:** For production or sensitive data, always use authentication and HTTPS with Ngrok.

---

## ☁️ Deploying to the Cloud

1. **Build your image:**
   ```sh
   docker build -t myapp .
   ```
2. **For different CPU architectures:**
   ```sh
   docker build --platform=linux/amd64 -t myapp .
   ```
3. **Push to your registry:**
   ```sh
   docker push myregistry.com/myapp
   ```
4. See Docker's [getting started guide](https://docs.docker.com/go/get-started-sharing/) for more details.

---

## 🧹 Stopping & Cleaning Up

- Stop all services:
  ```sh
  docker compose down
  ```
- Remove all volumes (optional, will delete all data!):
  ```sh
  docker compose down -v
  ```

---

## 🧪 Troubleshooting

- **Service not starting?**
  - Check logs: `docker compose logs -f`
  - Ensure required ports (8000, 8001, 11434, 3000) are free.
  - Check `.env` for correct values.
- **CORS errors?**
  - Make sure `CORS_ALLOW_ORIGIN` matches your frontend URL.
- **Ngrok not working?**
  - Check your firewall and Ngrok token.
  - Use the correct port in the command.
- **Ollama connection issues in Docker?**
  - See [open-webui/TROUBLESHOOTING.md](open-webui/TROUBLESHOOTING.md) for Docker networking tips.

---

## 📚 References
- [Docker's Python guide](https://docs.docker.com/language/python/)
- [ChromaDB Getting Started](https://docs.trychroma.com/docs/overview/getting-started)
