# RAG Distributed Async Queue API

This repository implements a **Retrieval-Augmented Generation (RAG)** system with distributed asynchronous processing.  
It combines **FastAPI**, **Redis RQ workers**, **MongoDB**, **Qdrant**, and **Cloudflare R2** to support scalable PDF ingestion, vector storage, and chat-based retrieval.

---

## 🚀 Features

- **User Authentication**
  - JWT-based authentication with signup/login endpoints
  - Secure password hashing (bcrypt)
- **PDF Upload & Processing**

  - Upload PDFs, stored securely in Cloudflare R2
  - Background processing via RQ workers
  - Text extraction & chunking using LangChain
  - Embedding generation via OpenAI embeddings
  - Storage into **Qdrant vector database**

- **Chat API**

  - Query documents asynchronously
  - Retrieve relevant chunks from Qdrant
  - Streamlined LLM response generation (via OpenAI Chat API)
  - Conversation history saved in MongoDB

- **Distributed Queue Processing**

  - Redis/Valkey used as job queue backend
  - RQ workers for scalable background execution

- **Devcontainer Ready**
  - Pre-configured `.devcontainer` setup for VS Code
  - Includes MongoDB, Qdrant, and Valkey services via Docker Compose

---

## 📂 Project Structure

```
madhavarora03-rag-distributed-async-queue-api/
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── app/
│   ├── main.py             # FastAPI entrypoint
│   ├── core/               # Config, security, utils
│   ├── queue/              # Redis/RQ setup
│   ├── routers/            # API routers (auth, upload, chat)
│   └── services/           # DB & Cloudflare R2 integrations
└── .devcontainer/          # Devcontainer + Docker setup
```

---

## ⚙️ Setup

### 1️⃣ Clone Repo & Enter Directory

```bash
git clone https://github.com/madhavarora03/rag-distributed-async-queue-api.git
cd rag-distributed-async-queue-api
```

### 2️⃣ Setup Environment

Copy `.env.example` → `.env` and fill in values:

```env
OPENAI_API_KEY=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
MONGO_USER=admin
MONGO_PASS=admin
MONGO_HOST=mongodb
MONGO_PORT=27017
DB_NAME=ragdaq
QDRANT_URI=http://vector-db:6333
SECRET_KEY=supersecretkey
REDIS_HOST=valkey
REDIS_PORT=6379
```

### 3️⃣ Devcontainer (Recommended)

Open in **VS Code Remote Containers** → It will spin up MongoDB, Valkey, and Qdrant automatically.

### 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 5️⃣ Run FastAPI App

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6️⃣ Run Worker

```bash
rq worker --with-scheduler --url redis://valkey:6379
```

---

## 📡 API Endpoints

### 🔑 Auth

- `POST /api/auth` → Signup
- `POST /api/auth/token` → Login (returns JWT)

### 📤 Upload

- `POST /api/upload` → Upload PDF (background job started)
- `GET /api/upload/status/{job_id}` → Check job status

### 💬 Chat

- `POST /api/chat` → Ask a question (job queued)
- `GET /api/chat/result/{job_id}` → Get chat response

### 🩺 Health Check

- `GET /api/health` → Service status

---

## 🛠️ Tech Stack

- **FastAPI** → REST API framework
- **MongoDB** → Metadata & conversations storage
- **Qdrant** → Vector DB for embeddings
- **Redis/Valkey + RQ** → Distributed async queue
- **Cloudflare R2 (S3 API)** → File storage
- **LangChain + OpenAI** → Embeddings & retrieval
- **Docker + Devcontainer** → Development environment

---

## 📜 License

MIT License © 2025 Madhav Arora
