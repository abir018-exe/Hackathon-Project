# Last Mile Stabilizer

AI-Powered Hackathon Project Stabilization & Demo Reliability Platform

## Overview

Last Mile Stabilizer helps developers and hackathon teams transform unstable, incomplete, or unreliable software projects into tested and demo-ready applications.

## Features

- **Project Integration**: Upload ZIP files or connect GitHub repositories
- **Codebase Scanner**: Deep static analysis of languages, frameworks, dependencies, and issues
- **AI Intelligence**: Demo Survival Score, feature reliability, failure predictions
- **Automated Stabilization**: AI-generated patches with human approval workflow
- **Demo Mode**: Isolated demo environment with mocks and fallbacks
- **Risk Monitor**: Git commit analysis, demo path protection, freeze mode
- **Testing**: Automated smoke tests, API tests, happy path validation
- **Demo Script Generator**: AI-powered presentation preparation
- **Team Workspace**: Collaboration with role-based permissions

## Tech Stack

### Frontend
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui (Radix UI)
- Framer Motion
- Recharts
- React Flow
- Zustand (state management)
- TanStack Query (data fetching)

### Backend
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Redis + Celery (background jobs)
- Pydantic v2
- Python-JOSE (JWT)
- OpenAI/Anthropic SDKs

### Analysis
- Tree-sitter (multi-language parsing)
- Python AST
- Custom rule-based scanning
- GitPython

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Using Docker Compose (Recommended)

1. Clone the repository
2. Copy environment file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` with your configuration (API keys, etc.)
4. Start all services:
   ```bash
   docker-compose up -d
   ```
5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env
alembic upgrade head
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local
npm run dev
```

#### Celery Workers
```bash
cd backend
source venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=info
celery -A app.workers.celery_app beat --loglevel=info
```

## Project Structure

```
last-mile-stabilizer/
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # React components
│   │   │   ├── ui/         # shadcn/ui components
│   │   │   └── layout/     # Layout components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Utilities
│   │   ├── store/          # Zustand store
│   │   ├── types/          # TypeScript types
│   │   └── styles/         # Global styles
│   └── ...
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API routes
│   │   ├── core/           # Core config, security
│   │   ├── db/             # Database session
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── workers/        # Celery tasks
│   └── ...
├── shared/                   # Shared types (future)
├── docker-compose.yml
└── README.md
```

## Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret (min 32 chars)
- `GITHUB_CLIENT_ID/SECRET` - GitHub OAuth
- `AI_PROVIDER` - "openai" or "anthropic"
- `AI_API_KEY` - AI provider API key

## API Documentation

Once running, visit http://localhost:8000/docs for interactive Swagger UI.

## Security

- All code execution in isolated Docker containers
- No execution of uploaded code during scanning
- Human approval required for all code modifications
- Complete audit trail of all changes
- Secret detection and alerting
- Role-based access control

## License

MIT License - see LICENSE file for details.