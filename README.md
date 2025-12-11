# FastAPI Calculator

A FastAPI back-end that implements user registration/login and calculation CRUD (BREAD) with integration tests and CI/CD.

This repository contains the code used for the Module 12 submission (branch: `module-12-submission`).

## Key Features

- User registration (`POST /users/register`) and login (`POST /users/login`) with bcrypt password hashing
- Calculation BREAD endpoints (`/calculations`) supporting create, browse, read, update, and delete
- SQLAlchemy ORM models and Pydantic v2-compatible schemas
- Integration tests that run against a PostgreSQL service in GitHub Actions
- Docker Compose for local testing and a GitHub Actions workflow that builds and (optionally) pushes a Docker image

# FastAPI Calculator

A small FastAPI service that implements user registration/login and CRUD operations for calculations persisted in PostgreSQL.

This repository contains the application source, tests, and container configuration used for Module 12.

Key features
- User registration and authentication with secure password hashing.
- Calculation BREAD (create, browse, read, update, delete).
- SQLAlchemy ORM and Pydantic v2-compatible schemas.
- Automated tests (pytest) and CI for continuous verification.

Repository layout (top-level)
- `app/` — application code (endpoints, models, schemas, operations).
- `tests/` — unit and integration tests.
- `sql/` — database initialization scripts.
- `docker-compose.yml`, `Dockerfile` — container configuration for local development and testing.
- `DOCUMENTATION.md` — project write-up and details for the Module 12 submission.

Quick run
- With Docker Compose: `docker-compose up --build`
- Run tests: `pytest -q`

Notes
- This README is a concise project overview. More detailed write-ups and submission artifacts are maintained separately in `DOCUMENTATION.md`.
```
