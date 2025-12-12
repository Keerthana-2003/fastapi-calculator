# FastAPI Calculator — Final Submission (Modules 9–14 + Final Feature)

## Project Overview

The FastAPI Calculator is a full-stack web application that combines a robust Python backend with a clean, functional front-end interface. The project was developed iteratively, with each module building upon the previous one to create a cohesive, production-ready application.

### Key Features

The application implements secure user authentication using JSON Web Tokens, ensuring that sensitive operations require valid credentials. Users can register accounts with unique usernames and email addresses, with passwords securely hashed using the bcrypt algorithm before storage. The calculation engine supports four fundamental mathematical operations—addition, subtraction, multiplication, and division—with proper validation to prevent errors such as division by zero.

The front-end interface provides intuitive forms for user registration, login, calculation management, and profile updates. All forms include client-side validation to provide immediate feedback to users before server requests are made. The application stores JWT tokens in the browser's localStorage, enabling persistent authentication across page refreshes.

### Repository Structure

```
fastapi-calculator/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and route definitions
│   ├── database.py          # SQLAlchemy models and database configuration
│   ├── schemas.py           # Pydantic schemas for request/response validation
│   ├── security.py          # Password hashing and JWT token management
│   ├── operations.py        # Core mathematical operation functions
│   ├── calculation_factory.py  # Factory pattern for calculation operations
│   └── static/
│       ├── register.html    # User registration page
│       ├── login.html       # User login page
│       ├── calculations.html # Calculation BREAD interface
│       └── profile.html     # User profile management page
├── tests/
│   ├── __init__.py
│   ├── test_operations.py   # Unit tests for mathematical operations
│   ├── test_security.py     # Unit tests for password hashing
│   ├── test_schemas.py      # Unit tests for Pydantic schema validation
│   ├── test_main.py         # API endpoint tests
│   ├── test_user_integration.py      # User route integration tests
│   ├── test_calculation_integration.py # Calculation integration tests
│   ├── test_calculation_model.py     # Calculation model tests
│   └── test_e2e.py          # Playwright end-to-end tests
├── sql/
│   └── init_db.sql          # Raw SQL statements for Module 9
├── .github/
│   └── workflows/
│       └── python-app.yml   # GitHub Actions CI/CD workflow
├── docker-compose.yml       # Multi-container Docker configuration
├── Dockerfile               # Application container definition
├── requirements.txt         # Python dependencies
├── wait_for_db_and_run.sh   # Database readiness script
└── README.md                # Project documentation (this file)
```

## What This Repo Contains
- FastAPI app with SQLAlchemy models, Pydantic v2 schemas, JWT authentication, and calculation BREAD routes.
- Static front-end pages for registration, login, calculation BREAD, and profile/password management.
- pytest suite (unit, integration, E2E with Playwright) wired for Postgres in CI and Docker.
- Dockerfile and docker-compose for local development; GitHub Actions workflow for automated tests and image publishing.

## Module-by-Module Deliverables
- **Module 9 – Raw SQL + Docker:** docker-compose brings up FastAPI, Postgres, and optional pgAdmin (port 5050). SQL walkthrough in `sql/init_db.sql` mirrors create/insert/query/update/delete steps; pgAdmin Query Tool used for screenshots (placeholders below).
- **Module 10 – Secure Users + CI/CD:** Added SQLAlchemy `User` model with hashed passwords and uniqueness constraints; Pydantic `UserCreate`/`UserRead`; bcrypt hashing helpers; unit/integration tests; CI builds/tests then pushes image to Docker Hub.
- **Module 11 – Calculation Domain:** Added `Calculation` model, validation (zero-divisor guard), and factory pattern for operations (add/subtract/multiply/divide). Unit/integration tests cover routing and persistence.
- **Module 12 – User & Calculation Routes:** FastAPI routes for user register/login and calculation BREAD. Integration tests validate happy/error paths. CI continues to publish on green.
- **Module 13 – JWT + Front-End + Playwright:** `/register` and `/login` issue JWTs; `register.html` and `login.html` perform client-side validation and store tokens. Playwright covers positive/negative auth flows.
- **Module 14 – Auth’d Calculations + UI:** Calculation endpoints require JWT (still accept `user_id` for backward compatibility). `calculations.html` supports create/browse/update/delete with client validation. Playwright covers BREAD happy/negative paths.
- **Final Feature – Profile Management:** `/me` and `/me/password` allow viewing/updating username/email and changing passwords while refreshing JWT. `profile.html` provides UI with client validation. Integration + E2E tests validate the flow end-to-end.

## Quickstart (Docker Compose)
1) Build and start API + Postgres (+ pgAdmin):
```bash
docker compose up --build
```
2) API docs: http://localhost:8000/docs
3) pgAdmin: http://localhost:5050 (host: db, user: postgres, pass: postgres, db: fastapi_db)
4) Replay Module 9 SQL: open pgAdmin Query Tool, paste statements from `sql/init_db.sql`.

Common Docker tasks:
- Rebuild API only: `docker compose up --build api`
- One-off shell: `docker compose run --rm api bash`
- Teardown with volumes: `docker compose down -v`

## Run Locally Without Docker
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_db
uvicorn app.main:app --reload
```

## Testing
- Unit/integration: `pytest -q`
- E2E (Playwright): `python -m playwright install chromium` then `pytest tests/test_e2e.py -q`
- CI runs Postgres-backed tests and Playwright; on success, builds and pushes Docker image.

## Front-End Pages
- Registration: http://localhost:8000/register.html
- Login: http://localhost:8000/login.html
- Calculations (BREAD): http://localhost:8000/calculations.html (JWT required)
- Profile (view/update email/username, change password): http://localhost:8000/profile.html (JWT required)
Tokens are stored in `localStorage.access_token`; client-side validation checks email format and password length.

## API Documentation

### Complete Endpoint Reference

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | / | Health check, returns welcome message | No |
| POST | /register | Register new user, returns JWT | No |
| POST | /login | Authenticate user, returns JWT | No |
| GET | /me | Get current user profile | Yes |
| PUT | /me | Update username/email | Yes |
| POST | /me/password | Change password | Yes |
| POST | /users/register | Register user (legacy) | No |
| POST | /users/login | Login user (legacy) | No |
| GET | /users/{id} | Get user by ID | No |
| GET | /calculations | Browse user's calculations | Yes |
| POST | /calculations | Create new calculation | Yes |
| GET | /calculations/{id} | Read specific calculation | Yes |
| PUT | /calculations/{id} | Update calculation | Yes |
| DELETE | /calculations/{id} | Delete calculation | Yes |
| GET | /add | Direct addition endpoint | No |
| GET | /subtract | Direct subtraction endpoint | No |
| GET | /multiply | Direct multiplication endpoint | No |
| GET | /divide | Direct division endpoint | No |

### Authentication Flow

1. User registers via POST /register with username, email, and password
2. Server validates input, hashes password, creates user record
3. Server returns JWT token with 1-hour expiration
4. Client stores token in localStorage
5. Subsequent requests include token in Authorization header: `Bearer <token>`
6. Server validates token, extracts user identity, processes request
7. Token refresh occurs on profile/password updates

## SQL Walkthrough
- SQL statements live in `sql/init_db.sql` (create tables, insert sample users/calculations, joins, update, delete).
- Run via pgAdmin Query Tool; capture screenshots of each step (table create, inserts, queries, update, delete).


## CI/CD Pipeline

### Pipeline Architecture

The GitHub Actions workflow automates the entire build, test, and deployment process. On every push or pull request to configured branches, the pipeline:

1. Checks out the repository code
2. Sets up Python 3.12 environment
3. Installs project dependencies from requirements.txt
4. Installs Playwright browsers for E2E testing
5. Starts a PostgreSQL service container
6. Runs the complete pytest suite including E2E tests
7. Builds the Docker image if tests pass
8. Pushes the image to Docker Hub with appropriate tags

### Workflow Configuration

The workflow file `.github/workflows/python-app.yml` defines the pipeline steps and service containers. The PostgreSQL service uses the official postgres:15 image with health checks ensuring the database is ready before tests run. Environment variables configure the database connection for both the service and application.

## Docker Integration
- Docker image: `keerthanam2k3/fastapi-calculator`. 
- Docker Hub link - https://hub.docker.com/repository/docker/keerthanam2k3/fastapi-calculator/general
- Manual publish (optional): `docker build -t keerthanam2k3/fastapi-calculator:local . && docker push keerthanam2k3/fastapi-calculator:local`

## Reflections and Learning Outcomes

### Technical Skills Developed

This project provided hands-on experience with modern Python web development practices. Working with FastAPI reinforced understanding of asynchronous programming concepts, dependency injection patterns, and automatic API documentation generation. The framework's integration with Pydantic demonstrated the power of type-driven development, where data validation and serialization emerge naturally from well-defined schemas.

SQLAlchemy ORM usage deepened understanding of the Active Record and Data Mapper patterns, transaction management, and relationship modeling. The progression from raw SQL in Module 9 to ORM in subsequent modules illustrated the tradeoffs between direct database control and abstraction convenience.

### Security Awareness

Implementing authentication from scratch—rather than using a pre-built solution—provided valuable insight into security fundamentals. Understanding how bcrypt generates salted hashes, why timing-safe comparison matters, and how JWT tokens enable stateless authentication creates a foundation for evaluating and implementing security measures in future projects.

The experience also highlighted the importance of defense in depth: client-side validation improves user experience but server-side validation is essential for security; HTTPS protects tokens in transit but secure storage practices matter at rest; password complexity rules help but rate limiting prevents brute force attacks.

### Testing Philosophy

Developing the three-tier testing strategy reinforced that different test types serve different purposes. Unit tests provide fast feedback during development and document expected behavior. Integration tests catch issues at component boundaries that unit tests miss. E2E tests verify the complete system works as users expect but run slowly and can be brittle.

The experience of maintaining tests alongside feature development demonstrated that tests are not overhead but investment. Well-written tests caught regressions immediately, documented intended behavior, and provided confidence when refactoring.

### DevOps Practices

Implementing CI/CD from the beginning established good habits around automated quality gates. The discipline of keeping tests passing, writing tests for new features before merging, and automating deployment reduces manual error and increases delivery confidence.

Docker containerization solved the "works on my machine" problem definitively. The same containers run locally, in CI, and in production, eliminating environment-specific bugs and simplifying onboarding for new developers.

### Areas for Future Improvement

The current implementation could be enhanced with rate limiting to prevent abuse, refresh tokens for better security than long-lived access tokens, email verification for new registrations, password reset functionality, and audit logging for sensitive operations. These would bring the application closer to production-ready standards for a real-world deployment.

The front-end could benefit from a JavaScript framework for better state management, improved accessibility features, responsive design testing, and internationalization support. These enhancements would improve user experience across different devices and locales.

---

## Conclusion

The FastAPI Calculator project successfully demonstrates full-stack web development competency through its progressive implementation across Modules 9-14 and the final feature. The application provides a solid foundation combining secure authentication, validated data handling, comprehensive testing, and automated deployment.

Key accomplishments include a clean separation of concerns between database models, business logic, and API routes; security-first design with hashed passwords and JWT authentication; comprehensive test coverage with unit, integration, and E2E tests; automated CI/CD pipeline publishing Docker images on every successful build; and responsive front-end interface with client-side validation.

The project demonstrates readiness for production deployment while maintaining code quality and security standards. The modular architecture supports future enhancements, and the established testing and deployment practices ensure changes can be made confidently.

This experience has reinforced the value of iterative development, automated testing, and infrastructure-as-code practices that will inform future software development efforts.
