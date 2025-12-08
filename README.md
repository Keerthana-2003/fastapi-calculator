# FastAPI Calculator

A FastAPI application with user authentication, password hashing, and PostgreSQL database.

## Features

- User registration and login with bcrypt password hashing
- SQLAlchemy ORM for database operations
- Pydantic input validation
- Calculator API (add, subtract, multiply, divide)
- PostgreSQL with Docker Compose
- Unit and integration tests
- GitHub Actions CI/CD pipeline
- Docker Hub deployment

## Project Structure

```
app/
  main.py           - FastAPI application and endpoints
  database.py       - SQLAlchemy models
  schemas.py        - Pydantic schemas
  security.py       - Password hashing
  operations.py     - Calculator logic

tests/
  test_security.py        - Password hashing tests
  test_schemas.py         - Schema validation tests
  test_user_integration.py - User endpoint tests
  test_main.py            - Calculator tests
```

## Setup and Run

### Using Docker Compose

```bash
git clone https://github.com/Keerthana-2003/fastapi-calculator.git
cd fastapi-calculator
docker-compose up --build
```

Access:
- FastAPI: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (admin@admin.com / admin)

### Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run application:
```bash
uvicorn app.main:app --reload
```

## Running Tests

```bash
pytest tests/ --ignore=tests/test_e2e.py -v
```

Expected: 54 tests passing

## Database Models

**users table**
- id (Primary Key)
- username (unique)
- email (unique)
- password_hash (bcrypt)
- created_at (timestamp)

**calculations table**
- id (Primary Key)
- operation
- operand_a, operand_b
- result
- timestamp
- user_id (Foreign Key)
