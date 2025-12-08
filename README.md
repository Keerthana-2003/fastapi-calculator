# FastAPI Calculator with Secure User Authentication

A FastAPI-based calculator application with secure user authentication, password hashing, and database integration using PostgreSQL.

## Features

- **User Authentication**: Secure registration and login with bcrypt password hashing
- **Database Integration**: SQLAlchemy ORM with PostgreSQL
- **Pydantic Validation**: Comprehensive input validation for all endpoints
- **Calculator API**: Add, subtract, multiply, and divide operations
- **RESTful API**: Full REST API with OpenAPI/Swagger documentation
- **Docker Support**: Containerized application with Docker Compose
- **CI/CD Pipeline**: Automated testing and Docker Hub deployment via GitHub Actions

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if running without Docker)
- Git

## Project Structure

```
fastapi-calculator/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application and endpoints
│   ├── database.py             # SQLAlchemy setup and models
│   ├── schemas.py              # Pydantic schemas for validation
│   ├── security.py             # Password hashing functions
│   ├── operations.py           # Calculator logic
│   └── calculator_*.py         # Additional utilities
├── tests/
│   ├── test_main.py            # Original calculator tests
│   ├── test_security.py        # Password hashing tests
│   ├── test_schemas.py         # Schema validation tests
│   └── test_user_integration.py# User registration/login tests
├── sql/
│   └── init_db.sql             # Database initialization script
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Getting Started

### Using Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Keerthana-2003/fastapi-calculator.git
   cd fastapi-calculator
   ```

2. **Start the application with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the services**:
   - **FastAPI Application**: http://localhost:8000
   - **API Documentation (Swagger UI)**: http://localhost:8000/docs
   - **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
   - **pgAdmin**: http://localhost:5050
     - Email: `admin@admin.com`
     - Password: `admin`

### Local Development (Without Docker)

1. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL**:
   - Create a database named `fastapi_db`
   - Update `DATABASE_URL` in `.env` if needed
   - Default: `postgresql://postgres:postgres@localhost:5432/fastapi_db`

4. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Run tests**:
   ```bash
   pytest -v
   ```

## API Endpoints

### User Management

#### Register a New User
```
POST /users/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password_123"
}
```

**Response (201 Created)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00"
}
```

#### User Login
```
POST /users/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure_password_123"
}
```

**Response (200 OK)**:
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

#### Get User Details
```
GET /users/{user_id}
```

### Calculator Operations

#### Add
```
GET /add?a=5&b=3
```
Response: `{"result": 8}`

#### Subtract
```
GET /subtract?a=5&b=3
```
Response: `{"result": 2}`

#### Multiply
```
GET /multiply?a=5&b=3
```
Response: `{"result": 15}`

#### Divide
```
GET /divide?a=6&b=3
```
Response: `{"result": 2}`

## Running Tests

### Run All Tests
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_security.py -v
pytest tests/test_schemas.py -v
pytest tests/test_user_integration.py -v
```

### Run Tests with Coverage
```bash
pytest --cov=app tests/
```

### Test Categories

1. **Security Tests** (`test_security.py`):
   - Password hashing functionality
   - Password verification
   - Hash uniqueness (salt verification)
   - Special characters and unicode support

2. **Schema Validation Tests** (`test_schemas.py`):
   - User creation validation
   - Email format validation
   - Password strength validation
   - Calculator operation validation
   - Division by zero prevention

3. **Integration Tests** (`test_user_integration.py`):
   - User registration with valid/invalid data
   - Duplicate username/email detection
   - User login with correct/incorrect credentials
   - Get user by ID
   - All calculator endpoints

## Database Models

### User Model
```python
class User(Base):
    id: int (Primary Key)
    username: str (Unique, 50 chars max)
    email: str (Unique, 100 chars max)
    password_hash: str
    created_at: datetime
```

### Calculation Model
```python
class Calculation(Base):
    id: int (Primary Key)
    operation: str
    operand_a: float
    operand_b: float
    result: float
    timestamp: datetime
    user_id: int (Foreign Key)
```

## Security Features

1. **Password Hashing**: bcrypt with automatic salt generation
2. **Email Validation**: Email format validation using Pydantic
3. **Unique Constraints**: Database-level and application-level validation
4. **Password Verification**: Constant-time comparison to prevent timing attacks
5. **Input Validation**: Comprehensive Pydantic schemas for all inputs

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

1. **Test Stage**:
   - Runs on every push and pull request
   - Spins up PostgreSQL container
   - Runs all tests (unit, integration, and E2E)
   - Checks code quality

2. **Build & Deploy Stage**:
   - Builds Docker image on successful tests
   - Pushes image to Docker Hub
   - Tags with commit SHA and 'latest'

### GitHub Secrets Required

Add these secrets to your GitHub repository:
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password/token

### Docker Hub Repository

Images are pushed to:
- `Keerthanam2k3/fastapi-calculator:latest`
- `Keerthanam2k3/fastapi-calculator:{commit-sha}`

**Pull the latest image**:
```bash
docker pull Keerthanam2k3/fastapi-calculator:latest
docker run -p 8000:8000 Keerthanam2k3/fastapi-calculator:latest
```

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fastapi_db
PYTHONUNBUFFERED=1
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>

# Or change the port in docker-compose.yml
ports:
  - "8001:8000"
```

### Database Connection Issues

1. Ensure PostgreSQL is running:
   ```bash
   docker ps  # Check if postgres container is running
   ```

2. Check connection string in docker-compose.yml or .env

3. Verify credentials match

### Test Failures

1. Clear pytest cache:
   ```bash
   pytest --cache-clear
   ```

2. Run with verbose output:
   ```bash
   pytest -vv
   ```

3. Check for port conflicts with Docker containers

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes and commit:
   ```bash
   git add .
   git commit -m "Add feature description"
   ```

3. Push to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request

5. GitHub Actions will automatically run tests

6. On merge, Docker image is pushed to Docker Hub

## Dependencies

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **sqlalchemy**: ORM
- **psycopg2-binary**: PostgreSQL adapter
- **pydantic**: Data validation
- **bcrypt**: Password hashing
- **passlib**: Password utilities
- **python-dotenv**: Environment variables
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **playwright**: E2E testing

## Learning Outcomes

This project demonstrates:

- ✅ **CLO3**: Create Python applications with automated testing
- ✅ **CLO4**: Set up GitHub Actions for CI/CD
- ✅ **CLO9**: Apply containerization with Docker
- ✅ **CLO10**: Create and test REST APIs
- ✅ **CLO11**: Integrate Python with SQL databases
- ✅ **CLO12**: Serialize and validate JSON with Pydantic
- ✅ **CLO13**: Implement secure authentication with password hashing

## Module 10 Submission

**GitHub Repository**: [fastapi-calculator](https://github.com/Keerthana-2003/fastapi-calculator)

**Docker Hub Repository**: [Keerthanam2k3/fastapi-calculator](https://hub.docker.com/r/Keerthanam2k3/fastapi-calculator)

**Key Implementations**:
1. ✅ SQLAlchemy User model with unique constraints
2. ✅ Password hashing with bcrypt
3. ✅ Pydantic schemas (UserCreate, UserRead, UserLogin)
4. ✅ User registration endpoint with validation
5. ✅ User login endpoint with password verification
6. ✅ Comprehensive unit tests (security, schemas)
7. ✅ Integration tests for user endpoints
8. ✅ GitHub Actions CI/CD pipeline with Docker Hub push

## Future Modules

- **Module 11**: Calculation model and factory pattern
- **Module 12**: BREAD endpoints for calculations
- **Module 13**: JWT authentication and frontend pages
- **Module 14**: Complete BREAD functionality in frontend

## License

This project is part of an academic assignment and is provided as-is for educational purposes.

## Contact

For questions or issues, please create an issue in the repository or contact the project owner.
