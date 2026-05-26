# Platform Architecture

## Overview

The DevSecOps Quality Automation Platform is a monorepo cloud-native system combining repository integration, scan orchestration, pipeline execution, quality gates, and observability.

## Layers

| Layer | Technology | Responsibility |
|-------|------------|----------------|
| Presentation | Next.js 14, React, Tailwind | Dashboards, auth UI, reports |
| API | FastAPI, Pydantic | REST APIs, webhooks, OAuth |
| Domain | Services + Repositories | Business logic, RBAC |
| Data | PostgreSQL, SQLAlchemy | Persistence, analytics |
| Async | Redis, Celery | Scan jobs, notifications |
| Observability | Prometheus, Grafana | Metrics, trends |
| Quality | SonarQube, ESLint, etc. | Static analysis |

## Data Flow

1. Developer pushes code → webhook → `POST /api/webhooks/github`
2. Backend creates `Pipeline` record → Celery task `run_pipeline`
3. Worker runs stages: lint → SAST → test → coverage → SonarQube
4. Results parsed → `Vulnerability`, `QualityMetric`, `ScanReport` persisted
5. Quality gate evaluated → pipeline status updated
6. Prometheus metrics incremented → Grafana dashboards refresh

## RBAC Matrix

| Permission | Admin | Developer | Security Analyst | Manager |
|------------|-------|-----------|------------------|---------|
| Manage orgs | ✓ | | | |
| Manage users | ✓ | | | |
| Connect repos | ✓ | ✓ | | |
| Run pipelines | ✓ | ✓ | | |
| View vulns | ✓ | ✓ | ✓ | ✓ |
| Suppress vulns | ✓ | | ✓ | |
| View analytics | ✓ | ✓ | ✓ | ✓ |
| Export reports | ✓ | ✓ | ✓ | ✓ |

## Deployment Modes

- **Local**: `docker compose up`
- **Kubernetes**: `kubectl apply -k k8s/`
- **Helm**: `helm install platform k8s/helm/platform`
