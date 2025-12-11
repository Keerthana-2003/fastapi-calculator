# FastAPI Calculator - Module 11 Implementation

## Overview

This document describes the implementation of Module 11: Calculation Model with Pydantic validation, factory pattern, and testing.

## Implementation Summary

### Focus for Module 11
This module adds focused work on the Calculation data model, validation, and testing. Key points:

- Calculation Model: `app/database.py` already defines the `Calculation` SQLAlchemy model with fields `id`, `operation`, `operand_a`, `operand_b`, `result`, `timestamp`, and `user_id` (FK to `users.id`). Cascade delete is configured.
- Pydantic Schemas: `app/schemas.py` contains `CalculationCreate` and `CalculationRead` with validation (allowed operation types and division-by-zero checks). Schemas now use Pydantic v2-compatible `model_config`.
- Factory: `app/calculation_factory.py` maps operation strings to functions in `app/operations.py` and exposes `compute`.

### Testing
Module 11 adds targeted tests for the calculation model and factory:

- Unit tests: `tests/test_operations.py`, `tests/test_schemas.py` validate operation logic and schema validation.
- Integration tests: `tests/test_calculation_integration.py` inserts a `Calculation` record into an in-memory SQLite DB and verifies persistence and relationships.

All tests (now 56 total) pass locally.

### Docker Deployment
Multi-container setup using Docker Compose:
- FastAPI service (Python 3.11, Uvicorn)
- PostgreSQL 15 database
- pgAdmin 4 for database management
- Health check script to wait for database readiness before starting app
- All services automatically initialized on startup

### CI/CD Pipeline
GitHub Actions workflow:
- Runs on push/pull requests to main, docker-postgres-setup, and module-10-submission branches
- PostgreSQL service container for testing
- Executes all 54 tests
- Builds and pushes Docker image to Docker Hub

## Architecture

### Project Structure
```
app/
  __init__.py           - Package marker
  main.py              - FastAPI application and endpoints
  database.py          - SQLAlchemy setup and models
  schemas.py           - Pydantic validation schemas
  security.py          - Password hashing functions
  operations.py        - Calculator operation logic

tests/
  __init__.py          - Package marker
  test_main.py         - Calculator endpoint tests
  test_operations.py   - Operation logic tests
  test_schemas.py      - Pydantic validation tests
  test_security.py     - Password hashing tests
  test_user_integration.py - User endpoint integration tests
  test_e2e.py          - End-to-end browser tests

docker-compose.yml     - Container orchestration
Dockerfile            - FastAPI application image
wait_for_db_and_run.sh - Startup script for DB health check
requirements.txt      - Python dependencies
```

### API Endpoints

**User Management:**
- POST /users/register - Create new user account
- POST /users/login - Authenticate user
- GET /users/{id} - Get user profile by ID

**Calculator:**
- POST /add - Add two numbers
- POST /subtract - Subtract two numbers
- POST /multiply - Multiply two numbers
- POST /divide - Divide two numbers

### Testing Results

All 56 tests passing locally (unit + integration; e2e excluded). The new integration tests validate DB persistence for `Calculation` records.
## Verification

### Cloud Codespace / Local Testing
Run tests:
```
pytest tests/ --ignore=tests/test_e2e.py -v
```

To run only Module 11 tests:
```
pytest tests/test_schemas.py tests/test_operations.py tests/test_calculation_integration.py -q
```

### Docker Compose
Start services if you want to test with Postgres instead of in-memory DBs:
```
docker-compose up --build
```

Access Swagger UI at http://localhost:8000/docs
## Deployment

### Docker Hub
Image pushed to Docker Hub repository:
- Repository: Keerthanam2k3/fastapi-calculator
- Tags: latest, commit SHA

![alt text](image-4.png)

### CI/CD Status

![alt text](image-5.png)

## Security Features

- Bcrypt password hashing with automatic salt
- Password verification using constant-time comparison
- Input validation for all user inputs
- Email format validation
- SQL injection prevention via SQLAlchemy ORM
- Unique constraints on username and email

## Dependencies

- FastAPI 0.109.0
- Uvicorn 0.27.0
- SQLAlchemy 2.0.23
- psycopg2-binary 2.9.9 (PostgreSQL driver)
- bcrypt 4.1.1
- passlib 1.7.4
- email-validator 2.1.0
- pytest 7.4.0
- pytest-asyncio 0.21.0
- playwright 1.40.0

## Running the Application

### Development
```
docker-compose up --build
```

The application will:
1. Start PostgreSQL database
2. Initialize database schema
3. Start FastAPI application
4. Be available at http://localhost:8000

### Access Points
- API Documentation: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (admin@admin.com / admin)
- Database: localhost:5432

## Notes

- Database is persisted in a Docker volume (postgres_data)
- Application uses environment variable DATABASE_URL for connection string
- All operations are logged to console
- E2E tests are skipped in CI/CD (require running server)
