# fastapi-ai-microservices

![Tests](https://github.com/pranavmag/fastapi-ai-microservices/actions/workflows/test.yml/badge.svg)

A scalable, microservices-based AI note-taking platform. Backend engineered with Python FastAPI to handle semantic search, JWT authentication, and high-concurrency async tasks.

# 🧠 AI-Powered Microservices Note-Taking API

## 📖 Project Overview
This repository hosts the backend infrastructure for a **microservices-based AI note-taking platform**. The system is engineered to handle semantic search (RAG), high-concurrency async tasks, and secure user authentication.

The goal is to move beyond "tutorial hell" and implement production-grade patterns: **CI/CD pipelines, Docker containerization, and AWS EC2 deployment.**

Demo 1 Link(Week 4): https://www.youtube.com/watch?v=lnzg8ZhjM8E 

**Current Status:** Phase 3 (Intelligence & Performance)

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

### Part 1: The Professional Foundation
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
- [x] **Week 3: Containerization (Docker) and Cloud Deployment (AWS)**
    - [x] Create `Dockerfile` for the API.
    - [x] Set up `docker-compose` for local development.
    - [x] Provision AWS EC2 Free Tier instance.
    - [x] Deploy containerized application via SSH.

### Part 2: Identity & Security
Focus: Authentication protocols, database migrations, and CI/CD pipelines.
- [x] **Week 4: Authentication (JWT)**
    - [x] Implement PyJWT for stateless token generation.
    - [x] Create protected routes (No token = No data).
- [x] **Week 5: Database Migrations (Alembic) & CI/CD (GitHub Actions)**
    - [x] Configure Alembic for schema evolution.
    - [x] Perform "add column" migration without data loss.
    - [x] Create `.github/workflows/test.yml`.
    - [x] Automate `pytest` execution on every push to `main`.
- [x] **Week 6 Part 1: Observability (Logging)**
    - [x] Implement structured logging (`structlog`) for production debugging.

### Part 3: Intelligence & Performance
Focus: Integrating LLMs, vector search, and performance optimization.
- [ ] **Week 6 Part 2: Applied AI (RAG Pipeline)**
    - [ ] Integrate OpenAI/Anthropic API.
    - [ ] Auto-generate summaries on note creation.
- [ ] **Week 7: Vector Database (Pinecone)**
    - [ ] Implement semantic search (finding notes by meaning, not keywords).
- [ ] **Week 8: Async Workers (Celery)**
    - [ ] Offload AI processing to background workers.
- [ ] **Week 9: Caching & Rate Limiting**
    - [ ] Implement Redis caching for read-heavy endpoints.
    - [ ] Add rate limiting (50 req/min) for API safety.

### Part 4: The Interface & Portfolio
Focus: Connecting the frontend and finalizing documentation.
- [ ] **Week 10: React Native Integration**
    - [ ] Build mobile Login & Feed screens.
- [ ] **Week 11: Mobile Polish & Chat UI**
    - [ ] Add the "Chat" interface. Make it feel responsive
- [ ] **Week 12: Technical Documentation**
    - [ ] Write "How I built a RAG pipeline" technical article.
- [ ] **Week 13: Final Deployment & Demo**

---

## 🚀 Getting Started (Local Dev)

1. **Clone the repo**
   ```bash
   git clone [https://github.com/ajaym/fastapi-ai-microservices.git](https://github.com/ajaym/fastapi-ai-microservices.git)
   cd fastapi-ai-microservices
