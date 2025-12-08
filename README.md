# FastAPI Calculator

A calculator API with user authentication built with FastAPI and PostgreSQL.

## Setup

### With Docker Compose
```bash
docker-compose up --build
```

Access at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (admin@admin.com / admin)

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest -v

# Start app
uvicorn app.main:app --reload
```

## API Endpoints

### User Registration
```
POST /users/register
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

### User Login
```
POST /users/login
{
  "email": "john@example.com",
  "password": "securepass123"
}
```

### Get User
```
GET /users/{user_id}
```

### Calculator
- `GET /add?a=5&b=3`
- `GET /subtract?a=5&b=3`
- `GET /multiply?a=5&b=3`
- `GET /divide?a=6&b=3`

## Project Structure

```
app/
  ├── main.py          # Routes and endpoints
  ├── database.py      # SQLAlchemy models and setup
  ├── schemas.py       # Pydantic schemas
  ├── security.py      # Password hashing
  └── operations.py    # Calculator logic

tests/
  ├── test_main.py     # Calculator tests
  ├── test_security.py # Password hashing tests
  ├── test_schemas.py  # Validation tests
  └── test_user_integration.py  # User endpoint tests
```

## Database

Tables: `users` and `calculations`

Users table has unique constraints on username and email.
Passwords are hashed with bcrypt before storage.

## Testing

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_security.py -v

# Run with coverage
pytest --cov=app tests/
```

## Requirements

- Python 3.11+
- PostgreSQL 15+
- Docker (optional)

## GitHub Actions CI/CD

Tests run automatically on push. On success, Docker image is pushed to Docker Hub.

Add these secrets to your repository:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`

Docker image: `Keerthanam2k3/fastapi-calculator:latest`
- **Module 12**: BREAD endpoints for calculations
- **Module 13**: JWT authentication and frontend pages
- **Module 14**: Complete BREAD functionality in frontend

## License

This project is part of an academic assignment and is provided as-is for educational purposes.

## Contact

For questions or issues, please create an issue in the repository or contact the project owner.
