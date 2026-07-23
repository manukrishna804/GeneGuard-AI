# 🧬 GeneGuard-AI - Team Setup Guide

Welcome to the GeneGuard-AI project!

Please follow **every step in order**. Do **not** skip any step.

---

# STEP 1: Install Git

Download Git:

https://git-scm.com/downloads

After installation, open Command Prompt and verify:

```bash
git --version
```

Example:

```
git version 2.50.1
```

---

# STEP 2: Install Docker Desktop

Download Docker Desktop

https://www.docker.com/products/docker-desktop/

Install Docker Desktop.

Restart your computer if required.

Open Docker Desktop.

Wait until Docker Desktop shows

```
Engine Running
```

Verify installation

```bash
docker --version

docker compose version
```

Both commands should display version information.

---

# STEP 3: Install VS Code

Download

https://code.visualstudio.com/

Install VS Code.

---

# STEP 4: Install VS Code Extensions

Install these extensions.

✅ Python

✅ Docker

✅ Pylance

(Optional)

GitLens

---

# STEP 5: Clone Repository

Open Command Prompt or PowerShell.

Go to the folder where you want the project.

Example

```bash
cd Desktop
```

Clone project

```bash
git clone <REPOSITORY_URL>
```

Example

```bash
git clone https://github.com/username/GeneGuard-AI.git
```

Go inside project

```bash
cd GeneGuard-AI
```

---

# STEP 6: Open in VS Code

Run

```bash
code .
```

OR

Open VS Code

File

Open Folder

Select

```
GeneGuard-AI
```

---

# STEP 7: Verify Folder Structure

You should see

```
GeneGuard-AI

backend/

frontend/

docker/

docker-compose.yml
```

If anything is missing, stop and contact the team.

---

# STEP 8: Start Docker Desktop

Before running the project

Docker Desktop MUST be running.

You should see

```
Engine Running
```

---

# STEP 9: Run Project

Open terminal inside VS Code.

Make sure terminal is at

```
GeneGuard-AI
```

Run

```bash
docker compose up --build
```

The first build may take **15–30 minutes**.

This is normal.

Do NOT stop the build.

---

# STEP 10: Verify Containers

Open another terminal.

Run

```bash
docker compose ps
```

Expected

```
geneguard-backend

geneguard-postgres

geneguard-pgadmin
```

Status should be

```
Up
```

---

# STEP 11: Open Swagger

Open browser

```
http://localhost:8000/docs
```

You should see

Swagger UI

Available APIs

```
GET /ping

POST /patients/

GET /patients/
```

---

# STEP 12: Test API

Click

POST /patients/

Try it out

Paste

```json
{
  "full_name":"Test User",
  "age":22,
  "gender":"Male",
  "email":"test@gmail.com"
}
```

Click Execute.

---

# STEP 13: Open pgAdmin

Browser

```
http://localhost:5050
```

Login

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

# STEP 14: Verify Database

Navigate

```
Servers

PostgreSQL

Databases

geneguard

Schemas

public

Tables
```

Tables should be

```
patients

wes_reports

phenotypes

lifestyles

family_histories

ai_reports
```

---

# STEP 15: Stop Project

When finished

Press

```
CTRL + C
```

inside terminal.

OR

Run

```bash
docker compose down
```

---

# STEP 16: Pull Latest Changes

Every day before starting work

Run

```bash
git pull origin main
```

Always pull latest changes before coding.

---

# STEP 17: Create Your Branch

Never work on main.

Example

```bash
git checkout -b feature/wes-module
```

Examples

```
feature/wes-module

feature/phenotype-module

feature/lifestyle-module

feature/family-history-module

feature/report-module
```

---

# STEP 18: Commit Changes

After completing work

```bash
git add .

git commit -m "Completed WES module"

git push origin feature/wes-module
```

Then create Pull Request.

---

# Important Rules

DO NOT modify

```
docker-compose.yml

Dockerfile

database/

main branch
```

Only work inside your assigned module.

---

# Folder Responsibility

Patient Module

```
app/models/patient.py
```

WES Module

```
app/models/wes.py
```

Phenotype Module

```
app/models/phenotype.py
```

Lifestyle Module

```
app/models/lifestyle.py
```

Family History

```
app/models/family_history.py
```

AI Reports

```
app/models/report.py
```

---

# Useful Commands

Start project

```bash
docker compose up --build
```

Run in background

```bash
docker compose up -d
```

Stop

```bash
docker compose down
```

Check containers

```bash
docker compose ps
```

View logs

```bash
docker compose logs backend
```

Rebuild

```bash
docker compose up --build
```

Pull latest code

```bash
git pull origin main
```

Current branch

```bash
git branch
```

Switch branch

```bash
git checkout branch-name
```

---

# Need Help?

If Docker doesn't start

→ Restart Docker Desktop.

If ports are already in use

→ Contact the project maintainer.

If APIs don't open

Run

```bash
docker compose ps
```

and share the output.

---

Happy Coding! 🚀