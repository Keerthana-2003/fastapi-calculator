# FastAPI Calculator

A FastAPI back-end that implements user registration/login and calculation CRUD (BREAD) with integration tests and CI/CD.

This repository contains the code used for the Module 12 submission (branch: `module-12-submission`).

## Key Features

- User registration (`POST /users/register`) and login (`POST /users/login`) with bcrypt password hashing
- Calculation BREAD endpoints (`/calculations`) supporting create, browse, read, update, and delete
- SQLAlchemy ORM models and Pydantic v2-compatible schemas
- Integration tests that run against a PostgreSQL service in GitHub Actions
- Docker Compose for local testing and a GitHub Actions workflow that builds and (optionally) pushes a Docker image

## Project Structure (high level)

```
app/
  main.py           - FastAPI application and endpoints (users + calculations)
  database.py       - SQLAlchemy models (User, Calculation)
  schemas.py        - Pydantic schemas
  security.py       - Password hashing helpers
  calculation_factory.py - Calculation compute logic

tests/
  test_user_integration.py - Integration tests for user and calculation endpoints (BREAD)
  test_operations.py       - Operation logic unit tests
  test_schemas.py          - Schema validation tests
  ...
```

## Setup and Run (Codespaces / Local)

Clone the repo and switch to the submission branch (if you are evaluating the submission):

```bash
git clone https://github.com/Keerthana-2003/fastapi-calculator.git
cd fastapi-calculator
git checkout module-12-submission
```

Using Docker Compose (recommended for tests and running with Postgres):

```bash
docker-compose up --build
```

Open the API docs (Swagger UI): http://localhost:8000/docs

### Local (without Docker)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Running Tests (integration + unit)

Run the full test suite (skip e2e):

```bash
pytest tests/ --ignore=tests/test_e2e.py -q
```

Expected on the `module-12-submission` branch: **70 tests passing** (unit + integration; e2e excluded).

Run only the calculation BREAD integration tests:

```bash
pytest tests/test_user_integration.py::TestCalculationBREAD -v
```

## Submission & Docker Hub

- Repository branch for Module 12 submission: `module-12-submission`
- Docker Hub image: replace the placeholder below with your Docker Hub repository if you publish an image during CI/CD:

```
docker pull <dockerhub-username>/fastapi-calculator:latest
```

## Manual checks via OpenAPI (what graders will verify)

1. Register a user via `POST /users/register` and confirm the user row is in the DB.
2. Create a calculation via `POST /calculations?user_id={id}` and verify the stored `result` and `user_id`.
3. Browse calculations with `GET /calculations?user_id={id}`.
4. Read/Update/Delete individual calculation resources via the corresponding endpoints and confirm appropriate status codes (404 for missing resources, 422 for invalid payloads).

## Notes

- This README is the repo-level documentation. The file `DOCUMENTATION.md` (in the same branch) contains the submission-specific writeup and screenshots to include with your submission.
- Do not include private guides or untracked personal instructions in the public repository when submitting to the course.
