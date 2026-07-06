# Enterprise Knowledge Assistant API

FastAPI backend for the Enterprise Knowledge Assistant. This is the boilerplate
scaffold — configuration, database wiring, logging, CORS, global exception
handling and a health endpoint are set up. Business logic is not implemented yet.

## Tech stack

- **FastAPI** — web framework
- **SQLAlchemy 2.x** — ORM
- **PostgreSQL** — database (via `psycopg2`)
- **Alembic** — database migrations
- **pydantic-settings** — `.env`-based configuration

## Project structure

```
enterprise-knowledge-assistant-api/
├── alembic/                    # Migration environment
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── app/
│   ├── main.py                 # App factory & entrypoint
│   ├── api/                    # Routers & dependencies
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   │           └── health.py
│   ├── core/                   # Config, logging, exceptions
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── exceptions.py
│   │   └── exception_handlers.py
│   ├── database/               # Engine, session, declarative base
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business-logic layer
│   ├── rag/                    # Retrieval-augmented generation
│   ├── agents/                 # Agentic workflows
│   └── utils/                  # Helpers
├── .env.example
└── requirements.txt
```

## Getting started

1. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create your environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

   Update the PostgreSQL credentials as needed.

4. Run the development server:

   ```powershell
   uvicorn app.main:app --reload
   ```

5. Open the interactive docs at http://localhost:8000/docs
   and the health check at http://localhost:8000/api/v1/health

## Database migrations (Alembic)

```powershell
# Autogenerate a new revision (after defining models & importing them in app/database/base.py)
alembic revision --autogenerate -m "your message"

# Apply migrations
alembic upgrade head
```

