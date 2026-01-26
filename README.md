# fastapi-ai-microservices
A scalable, microservices-based AI note-taking platform. Backend engineered with Python FastAPI to handle semantic search, JWT authentication, and high-concurrency async tasks.

# 🧠 AI-Powered Microservices Note-Taking API

## 📖 Project Overview
This repository hosts the backend infrastructure for a **microservices-based AI note-taking platform**. The system is engineered to handle semantic search (RAG), high-concurrency async tasks, and secure user authentication.

The goal is to move beyond "tutorial hell" and implement production-grade patterns: **CI/CD pipelines, Docker containerization, and AWS EC2 deployment.**

**Current Status:** Phase 1 (Foundation & Database Architecture)

---

## 🛠 Tech Stack (Planned & Implemented)
* **Core Backend:** Python, FastAPI, SQLModel (SQLAlchemy + Pydantic)
* **Database:** SQLite (Dev), PostgreSQL (Prod), Pinecone (Vector DB)
* **Asynchronous Workers:** Celery + Redis
* **Authentication:** PyJWT (stateless auth)
* **Infrastructure:** Docker, AWS EC2, GitHub Actions (CI/CD)
* **Frontend:** React Native (Mobile)

---

## 🗺 Engineering Roadmap (2026 Journey)

### Month 1: The Professional Foundation
Focus: Writing clean, tested code that adheres to strict typing and industry standards.
- [x] **Week 1: FastAPI & SQLModel**
    - [x] Implement strict typing with Pydantic schemas.
    - [x] Build `GET /notes` and `POST /notes` endpoints.
    - [x] Database persistence setup.
- [x] **Week 2: Automated Testing (pytest)**
    - [x] Configure `pytest` environment.
    - [x] Write integration tests for API endpoints (200 OK checks).
    - [x] Add 404 and 422 error tests
    - [x] Implement GET /notes/{id} endpoint
    - [x] Organize tests into multiple files
    - [x] Organize tests into test_create.py and test_read.py
    - [x] Add parametrized tests for validation scenarios
    - [x] Measure code coverage with pytest-cov
- [ ] **Week 3: Containerization (Docker)**
    - [x] Create `Dockerfile` for the API.
    - [ ] Set up `docker-compose` for local development.
- [ ] **Week 4: Cloud Deployment (AWS)**
    - [ ] Provision AWS EC2 Free Tier instance.
    - [ ] Deploy containerized application via SSH.

### Month 2: Identity & Security
Focus: Authentication protocols, database migrations, and CI/CD pipelines.
- [ ] **Week 5: Authentication (JWT)**
    - [ ] Implement PyJWT for stateless token generation.
    - [ ] Create protected routes (No token = No data).
- [ ] **Week 6: Database Migrations (Alembic)**
    - [ ] Configure Alembic for schema evolution.
    - [ ] Perform "add column" migration without data loss.
- [ ] **Week 7: CI/CD (GitHub Actions)**
    - [ ] Create `.github/workflows/test.yml`.
    - [ ] Automate `pytest` execution on every push to `main`.
- [ ] **Week 8: Observability (Logging)**
    - [ ] Implement structured logging (`structlog`) for production debugging.

### Month 3: Intelligence & Performance
Focus: Integrating LLMs, vector search, and performance optimization.
- [ ] **Week 9: Applied AI (RAG Pipeline)**
    - [ ] Integrate OpenAI/Anthropic API.
    - [ ] Auto-generate summaries on note creation.
- [ ] **Week 10: Vector Database (Pinecone)**
    - [ ] Implement semantic search (finding notes by meaning, not keywords).
- [ ] **Week 11: Async Workers (Celery)**
    - [ ] Offload AI processing to background workers.
- [ ] **Week 12: Caching & Rate Limiting**
    - [ ] Implement Redis caching for read-heavy endpoints.
    - [ ] Add rate limiting (50 req/min) for API safety.

### Month 4: The Interface & Portfolio
Focus: Connecting the frontend and finalizing documentation.
- [ ] **Week 13: React Native Integration**
    - [ ] Build mobile Login & Feed screens.
- [ ] **Week 14: Mobile Polish & Chat UI**
- [ ] **Week 15: Technical Documentation**
    - [ ] Write "How I built a RAG pipeline" technical article.
- [ ] **Week 16: Final Deployment & Demo**

---

## 🚀 Getting Started (Local Dev)

1. **Clone the repo**
   ```bash
   git clone [https://github.com/ajaym/fastapi-ai-microservices.git](https://github.com/ajaym/fastapi-ai-microservices.git)
   cd fastapi-ai-microservices
