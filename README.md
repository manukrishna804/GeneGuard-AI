# 🧬 GeneGuard-AI

GeneGuard-AI is an AI-powered Genetic Disorder Prediction and Clinical Decision Support System designed to assist in analyzing genetic data, patient phenotypes, lifestyle factors, and family history to generate explainable disease risk assessments.

This repository currently contains the **backend foundation**, including database architecture, Docker setup, API structure, and shared models for all project modules.

---

# 🚀 Tech Stack

## Backend
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic
- Uvicorn

## Database
- PostgreSQL 16
- pgAdmin 4

## Containerization
- Docker
- Docker Compose

## API Documentation
- Swagger UI
- OpenAPI

---

# 📁 Project Structure

```
GeneGuard-AI/

├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── crud/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── uploads/
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── Dockerfile
│   └── .env
│
├── frontend/
│
├── docker/
│
├── docker-compose.yml
│
└── README.md
```

---

# ✅ Current Features

Completed backend foundation includes:

- FastAPI Backend Setup
- PostgreSQL Database
- SQLAlchemy ORM
- Alembic Migration System
- Docker Configuration
- Docker Compose Configuration
- Environment Variable Management
- Swagger API Documentation
- Patient CRUD API
- Shared Database Architecture
- Foreign Key Relationships

---

# 🗄 Current Database Architecture

```
Patient
│
├── WES Reports
│
├── Phenotype
│
├── Lifestyle
│
├── Family History
│
└── AI Reports
```

Database Tables

```
patients

wes_reports

phenotypes

lifestyles

family_histories

ai_reports
```

All module tables are connected through

```
patient_id
```

---

# 👨‍💻 Team Module Allocation

Each team member should work ONLY inside their assigned module.

| Module | Folder |
|----------|----------------|
| Patient Management | app/models/patient.py |
| WES Analysis | app/models/wes.py |
| Phenotype Analysis | app/models/phenotype.py |
| Lifestyle Analysis | app/models/lifestyle.py |
| Family History | app/models/family_history.py |
| AI Reports | app/models/report.py |

Do NOT modify another module without discussion.

---

# ⚙️ Prerequisites

Install

- Git
- Docker Desktop
- VS Code (Recommended)

Docker Desktop must be running before starting the project.

---

# 📥 Clone Repository

```
git clone https://github.com/manukrishna804/GeneGuard-AI.git
```

Go into the project

```
cd GeneGuard-AI
```

---

# 🔧 Environment Setup

Inside

```
backend/
```

Create

```
.env
```

Example

```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/geneguard

SECRET_KEY=your-secret-key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

# ▶️ Run Project

From project root

```
docker compose up --build
```

First build may take several minutes because required AI packages are downloaded.

---

# 🌐 Application URLs

Backend

```
http://localhost:8000
```

Swagger Documentation

```
http://localhost:8000/docs
```

pgAdmin

```
http://localhost:5050
```

PostgreSQL

```
localhost:5432
```

---

# 🗃 pgAdmin Login

Email

```
admin@geneguard.com
```

Password

```
admin
```

(Use values from docker-compose.yml if different.)

---

# 📌 Existing APIs

## Health Check

```
GET /ping
```

---

## Patients

Create Patient

```
POST /patients/
```

Get Patients

```
GET /patients/
```

Swagger UI can be used to test APIs.

---

# 🗄 Database Migration

Whenever you change database models

Generate migration

```
cd backend

alembic revision --autogenerate -m "your message"
```

Apply migration

```
alembic upgrade head
```

Never manually create tables.

Always use Alembic migrations.

---

# 🌿 Git Workflow

Do NOT work directly on main.

Create your own branch.

Example

```
git checkout -b feature/wes-module
```

After completing your work

```
git add .

git commit -m "Completed WES module"

git push origin feature/wes-module
```

Create a Pull Request.

---

# 📂 Upload Folder

Patient reports and uploaded files will be stored in

```
backend/uploads/
```

Do NOT commit uploaded files.

---

# 🚫 Files Not To Commit

Do NOT push

```
.env

__pycache__/

.venv/

uploads/

*.pyc
```

---

# 📝 Coding Guidelines

- Follow existing project structure.
- Use SQLAlchemy ORM.
- Use Pydantic Schemas.
- Do not hardcode database credentials.
- Use Alembic for schema changes.
- Keep APIs inside app/api.
- Business logic should be inside app/services.
- Database operations should be inside app/crud.

---

# 📌 Current Development Status

✅ Backend Foundation Complete

✅ Docker Setup Complete

✅ Database Setup Complete

✅ Patient Module Complete

✅ Shared Database Architecture Complete

🚧 WES Analysis Module

🚧 Phenotype Analysis Module

🚧 Lifestyle Module

🚧 Family History Module

🚧 AI Report Generation

🚧 Authentication

🚧 AI Pipeline

---

# 🎯 Project Goal

GeneGuard-AI aims to provide an intelligent platform for genetic disorder analysis by integrating

- Whole Exome Sequencing (WES)
- Clinical Phenotype
- Lifestyle Factors
- Family Genetic History
- Explainable AI

to generate comprehensive disease risk reports and assist clinicians in making informed decisions.

---

