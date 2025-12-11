# FastAPI Calculator - Module 10 Implementation

## Overview

This document describes the implementation of Module 10: Secure User Model with Pydantic Validation, Database Testing, and Docker Deployment.

## Implementation Summary

### User Authentication System
Implemented a complete user management system with secure password handling:
- User registration endpoint (POST /users/register) with validation
- User login endpoint (POST /users/login) with password verification
- User profile retrieval endpoint (GET /users/{id})
- Passwords hashed using bcrypt with automatic salt generation
- Duplicate username and email detection
- Email format validation using email-validator

### Database Layer
Built SQLAlchemy ORM models for data persistence:
- Users table with columns: id, username, email, password_hash, created_at
- Unique constraints on username and email
- Calculations table linked to users with cascade delete
- Foreign key relationship between calculations and users
- Database initialization on application startup

### Input Validation
Pydantic schemas for request/response validation:
- UserCreate: username (3-50 characters, alphanumeric + underscore/dash), email, password (min 6 chars)
- UserRead: user response without password_hash
- UserLogin: email and password for authentication
- CalculationCreate and CalculationRead for operation validation

### Testing
54 comprehensive unit and integration tests covering:
- Password hashing and verification (7 tests)
- Pydantic schema validation (18 tests)
- User registration, login, and retrieval (19 tests)
- Calculator operations (10 tests)

All tests pass locally and in CI/CD pipeline.

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

## Testing Results

![alt text](image.png)
![alt text](image-6.png)

All 54 tests passing:
- test_security.py: 7 tests
- test_schemas.py: 18 tests
- test_user_integration.py: 19 tests
- test_main.py: 10 tests

## Verification

### Local Testing
Run tests locally:
```
pytest tests/ --ignore=tests/test_e2e.py -v
```

### Docker Compose
Start all services:
```
docker-compose up --build
```

Access Swagger UI at http://localhost:8000/docs

![alt text](image-1.png)

### User Registration Test
![alt text](image-2.png)

### User Login Test
![alt text](image-3.png)

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
