# FastAPI Calculator - Module 12 Implementation

## Overview

This document describes the implementation of Module 12: User & Calculation Routes with BREAD operations and comprehensive testing.

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

All tests (now 58 total) pass locally.

### Docker Deployment
### User Endpoints
- **POST /users/register** - Create new user with bcrypt password hashing and uniqueness validation
- **POST /users/login** - Authenticate user by verifying password against stored hash
- **GET /users/{id}** - Retrieve user profile information
- PostgreSQL 15 database
### Calculation Endpoints (BREAD)
All calculation endpoints accept `user_id` as a query parameter to enforce user-scoped operations and isolation.

- **POST /calculations** - Create a new calculation (Add). Accepts operation, operand_a, operand_b. Result is computed using CalculationFactory and validated with CalculationCreate schema.
- **GET /calculations** - Retrieve all calculations for the authenticated user (Browse). Returns list of CalculationRead objects.
- **GET /calculations/{id}** - Retrieve a specific calculation by ID (Read). Returns single CalculationRead object. Returns 404 if not found or owned by different user.
- **PUT /calculations/{id}** - Update an existing calculation (Edit). Accepts operation, operand_a, operand_b. Result is recomputed. Returns 404 if not found or owned by different user.
- **DELETE /calculations/{id}** - Delete a calculation (Delete). Returns 404 if not found or owned by different user.

### CI/CD Pipeline
Total: **70 tests passing** locally (verified with pytest).
- Runs on push/pull requests to `main`, `docker-postgres-setup`, `module-10-submission`, and `module-11-submission` branches
Test categories:
- **User registration/login**: 19 tests covering registration, duplicate emails, login success/failure
- **User endpoints**: 5 tests for GET /users/{id} with valid/invalid IDs
- **Calculation BREAD endpoints**: 15 integration tests covering Create, Browse, Read, Update, Delete, and error handling (404s for non-existent resources, 422 for validation errors, 400 for business logic)
- **Pydantic schema validation**: 18 tests for request/response schema validation
- **Password hashing**: 7 tests for bcrypt integration and security
- **Calculation model/factory**: 6 tests for SQLAlchemy Calculation model and CalculationFactory.compute()

All tests verify user isolation (users can only access/modify their own calculations).
- PostgreSQL service container for testing

### Project Structure
```
  security.py          - Password hashing functions
  operations.py        - Calculator operation logic
GitHub Actions workflow:
- Executes all 70 tests as part of CI (unit + integration; e2e excluded by default)
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
To run only Module 11 tests:
```
```
docker-compose up --build
```

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
