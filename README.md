# TrendFactory

**Project:** TrendFactory - AI-powered trend analysis platform
**Tech Stack:** Nuxt 3 + Django + PostgreSQL
**Deployment:** Render

## Overview

TrendFactory is a full-stack application built with:

- **Frontend:** Nuxt 3 (Vue 3 + Nitro)
- **Backend:** Django + Django REST Framework
- **Database:** PostgreSQL
- **Containerization:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Deployment:** Render

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (if not using Docker)

### Development with Docker

```bash
# Start all services
docker-compose up --build

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Backend Health: http://localhost:8000/health
```

### Development without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up PostgreSQL and update DATABASE_URL in environment
export DATABASE_URL=postgres://user:password@localhost:5432/trendfactory
export SECRET_KEY=your-secret-key

python manage.py migrate
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
.
├── frontend/           # Nuxt 3 application
│   ├── pages/         # Vue pages
│   ├── components/    # Vue components
│   └── Dockerfile
├── backend/           # Django application
│   ├── trendfactory/  # Django project
│   ├── api/          # Django app (API endpoints)
│   └── Dockerfile
├── docker-compose.yml
└── .github/workflows/
    └── ci.yml        # CI/CD pipeline
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/admin/` | GET | Django admin panel |

## Environment Variables

### Backend
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `DATABASE_URL` - PostgreSQL connection string
- `ALLOWED_HOSTS` - Comma-separated allowed hosts
- `CORS_ALLOWED_ORIGINS` - Comma-separated CORS origins

### Frontend
- `NUXT_PUBLIC_API_BASE` - Backend API URL

## Deployment to Render

### Web Service (Backend)

1. Create a new **Web Service** on Render
2. Connect your GitHub repository
3. Configure:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn trendfactory.wsgi:application`
4. Add environment variables
5. Deploy

### Static Site (Frontend)

1. Create a new **Static Site** on Render
2. Connect your GitHub repository
3. Configure:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `.output/public`
4. Add environment variable: `NUXT_PUBLIC_API_BASE`
5. Deploy

### PostgreSQL Database

1. Create a new **PostgreSQL** database on Render
2. Copy the internal connection string
3. Add to backend environment variables as `DATABASE_URL`

## CI/CD Pipeline

The GitHub Actions workflow includes:

- Frontend linting and type checking
- Frontend build verification
- Backend tests with PostgreSQL
- Security audits (npm audit, safety)
- Docker build verification

## Development Workflow

1. Create feature branch: `git checkout -b feature/name`
2. Make changes and commit
3. Push and create pull request
4. CI runs automatically
5. Merge after approval

## License

MIT
