# AEOS Deployment Guide 🚀

## Overview

This document explains how to deploy AEOS (AI Engineering Operating System) in a production environment.

---

# Server Requirements

Minimum:

- Ubuntu 22.04+
- 4GB RAM
- 2 CPU cores
- 20GB storage

Required software:

- Docker
- Docker Compose
- Git
- Python 3.12
- Node.js 20+

---

# Environment Configuration

Create environment file:
.env


Example:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/aeos_db

SECRET_KEY=your_secret_key

REDIS_URL=redis://localhost:6379
Docker Deployment

Build services:

docker compose up --build

Check containers:

docker ps
Database Setup

Run migrations:

alembic upgrade head

Verify database:

psql -U aeos_user -d aeos_db
Backend Deployment

Start FastAPI:

uvicorn app.main:app --host 0.0.0.0 --port 8000

Health check:

http://server-ip:8000/health
Frontend Deployment

Install dependencies:

npm install

Build:

npm run build

Start:

npm start
Nginx Configuration

Nginx routes:

Client
 |
Nginx
 |
----------------
|              |
Frontend    Backend
:3000        :8000
Production Checklist

✅ Database configured
✅ Environment variables added
✅ Docker containers running
✅ Backend health check passed
✅ Frontend build successful
✅ HTTPS enabled
✅ Admin login tested
✅ Student workflow tested

Backup

Database backup:

pg_dump aeos_db > backup.sql

Restore:

psql aeos_db < backup.sql
Future Improvements
Cloud deployment
CI/CD pipeline
Monitoring
Auto scaling

---

### Step 3: Save करा

```text
Ctrl + O
Enter
Ctrl + X
Step 4: Git push
git add docs/DEPLOYMENT.md

git commit -m "Add AEOS deployment checklist"

git push origin main
