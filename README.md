# DevSecOps Quality Automation Platform

Enterprise-grade cloud-native DevSecOps platform for automated code quality analysis, security scanning, CI/CD orchestration, and analytics dashboards.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Next.js    │────▶│   FastAPI    │────▶│ PostgreSQL  │
│  Frontend   │     │   Backend    │     └─────────────┘
└─────────────┘     └──────┬───────┘
                           │
                    ┌──────▼───────┐     ┌─────────────┐
                    │ Redis/Celery │────▶│ Scan Tools  │
                    └──────────────┘     └─────────────┘
┌─────────────┐     ┌──────────────┐
│ Prometheus  │◀────│   Metrics    │
└──────┬──────┘     └──────────────┘
       ▼
┌─────────────┐
│   Grafana   │
└─────────────┘
```

## Quick Start

```bash
# Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Start all services
docker compose -f docker/docker-compose.yml up --build
```

| Service    | URL                    |
|------------|------------------------|
| Frontend   | http://localhost:3000  |
| API        | http://localhost:8000  |
| API Docs   | http://localhost:8000/docs |
| Grafana    | http://localhost:3001  |
| Prometheus | http://localhost:9090  |
| SonarQube  | http://localhost:9000  |

Default admin (seeded on first run): `admin@platform.local` / `ChangeMe123!`

## Monorepo Structure

```
/frontend      Next.js dashboard
/backend       FastAPI application
/docker        Docker Compose & Dockerfiles
/k8s           Kubernetes manifests
/devops        Prometheus, Grafana, nginx
/scripts       Setup & utility scripts
/security-rules Semgrep custom rules
/docs          Architecture documentation
```

## Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
celery -A app.workers.celery_app worker -l info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Features

- GitHub & GitLab OAuth integration
- Repository management & webhooks
- Pipeline orchestration with quality gates
- ESLint, Pylint, Bandit, Semgrep, SonarQube scanning
- RBAC (Admin, Developer, Security Analyst, Manager)
- Analytics dashboards with historical metrics
- Audit logging & encrypted secrets

## License

MIT
