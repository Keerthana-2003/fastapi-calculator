# FastAPI Calculator

Production-ready FastAPI backend that progresses the Module 9–12 requirements (raw SQL exercises, secure user model, calculation domain modeling, and fully tested REST endpoints with CI/CD + Docker Hub deployment).

## Module Alignment
- **Module 9 – Raw SQL + Docker:** `docker-compose.yml` launches FastAPI, PostgreSQL, and optional pgAdmin (port 5050). The SQL walkthrough lives in `sql/init_db.sql` so every create/insert/query/update/delete statement can be replayed inside pgAdmin’s Query Tool.
- **Module 10 – Secure Users:** `app/security.py` hashes and verifies passwords with bcrypt, `app/schemas.py` provides `UserCreate`/`UserRead`, and `app/database.py` wires SQLAlchemy models + Alembic-ready metadata. Unit and integration tests under `tests/` assert hashing, schema validation, and uniqueness. GitHub Actions runs the full suite and builds the Docker image.
- **Module 11 – Calculation Domain:** `app/operations.py`, `app/calculation_factory.py`, and `app/calculator_memento.py` implement the optional factory pattern plus persistence-ready SQLAlchemy models + Pydantic schemas. Tests cover factory routing, validation, and DB commits.
- **Module 12 – User & Calculation Routes:** `app/main.py` exposes `/users` (register/login) and `/calculations` (BREAD). Integration tests (`tests/test_*integration.py`, `tests/test_e2e.py`) cover registration, login, and full calculation CRUD.
- **Module 13 – JWT + Front-End + Playwright:** `/register` and `/login` now issue JWTs, `app/static/register.html` and `app/static/login.html` provide client-side validation + token storage, and Playwright E2E covers positive/negative auth flows.
- **Module 14 – Auth’d Calculations + UI:** Calculation BREAD endpoints enforce JWT (still accept `user_id` for backward compatibility), partial updates are supported, and `app/static/calculations.html` provides a JWT-backed UI for create/browse/update/delete. Playwright now covers calc happy/negative paths.

## Repository Layout
- `app/` – FastAPI app, routers, models, factory logic, and security helpers.
- `tests/` – pytest suite (unit, integration, and end-to-end tests hitting a live Postgres container).
- `sql/` – raw SQL used during Module 9 verification (same statements provided in the assignment brief).
- `Dockerfile` & `docker-compose.yml` – containers for local dev + parity with CI.
- `requirements.txt` – locked versions for FastAPI, SQLAlchemy, Pydantic v2, psycopg, etc.
- `wait_for_db_and_run.sh` – helper entrypoint for Docker to block until Postgres is ready.
- `app/static/` – login, registration, and calculations pages with client-side validation and JWT storage.

## Prerequisites
- Docker + Docker Compose v2 (recommended path for Modules 9–12 verification).
- Python 3.11+ if you prefer running locally without containers.
- Make sure port 8000 (API) and 5050 (pgAdmin) are available.

## Quick Start (Docker Compose)
1. Copy `.env.example` → `.env` if provided, or export `POSTGRES_*` variables inline.
2. Build + start everything:
	 ```bash
	 docker compose up --build
	 ```
3. FastAPI will be reachable at http://localhost:8000/docs and pgAdmin at http://localhost:5050.
4. To reseed the DB with the Module 9 SQL, open pgAdmin → Query Tool → paste the statements from `sql/init_db.sql`.

### Common Docker Tasks
- Rebuild only the API: `docker compose up --build api`
- Run a one-off shell inside the API container: `docker compose run --rm api bash`
- Tear everything down (volumes included): `docker compose down -v`

## Running Locally Without Docker
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_db
alembic upgrade head  # if using migrations
uvicorn app.main:app --reload
```

## Testing Strategy
- **Unit tests:** `pytest tests/test_operations.py tests/test_security.py ...`
- **Integration tests:** `pytest tests/test_user_integration.py tests/test_calculation_integration.py`
- **End-to-end (Playwright):** `pytest tests/test_e2e.py` (chromium installed via Dockerfile/CI)

The CI workflow (see `.github/workflows/`) launches Postgres, runs every test target, and on success builds/pushes the Docker image so Docker Hub always mirrors the latest mainline commit (Module 10–12 deliverable).


## API Surface (excerpt)
| Method | Path | Description |
| ------ | ---- | ----------- |
| POST | `/register` | Register user and return JWT |
| POST | `/login` | Login and return JWT |
| POST | `/users/register` | Create a user with `username`, `email`, `password` |
| POST | `/users/login` | Validate credentials and return a session payload |
| GET | `/calculations` | Browse calculations (optionally filter by user) |
| POST | `/calculations` | Create a calculation using the factory |
| GET | `/calculations/{id}` | Read a single calculation |
| PUT | `/calculations/{id}` | Update operands or operation type |
| DELETE | `/calculations/{id}` | Remove a calculation |

## Docker Hub & CI/CD
- GitHub Actions workflow: `.github/workflows/ci.yml` (runs tests, builds image, pushes on main).
- Docker image tag convention: `YOUR_DOCKERHUB_USERNAME/fastapi-calculator:<git-sha>`.
- To manually publish from a dev machine:
	```bash
	docker build -t YOUR_DOCKERHUB_USERNAME/fastapi-calculator:local .
	docker push YOUR_DOCKERHUB_USERNAME/fastapi-calculator:local
	```

## Front-End Pages (Modules 13–14)
- Registration page: http://localhost:8000/register.html (served from `/static/register.html`).
- Login page: http://localhost:8000/login.html (served from `/static/login.html`).
- Calculations page: http://localhost:8000/calculations.html (served from `/static/calculations.html`), uses the JWT in `localStorage.access_token` to perform create/browse/update/delete.
- Tokens are stored in `localStorage` (`access_token`) on success. Client-side validation checks email format and minimum password length before sending requests.

## Running Playwright E2E
Playwright chromium is installed in the Docker image and CI. If running locally:
```bash
playwright install chromium
pytest tests/test_e2e.py -q
```
Ensure the database is available (`docker compose up -d`) before running tests; the test suite starts/stops `uvicorn` automatically.

### Module 14 Smoke Checklist
- Start services: `docker compose up --build` (or run locally with `uvicorn app.main:app --reload`).
- Open http://localhost:8000/calculations.html, login first (token saved in `localStorage`), then create/update/delete calculations.
- Run full suite: `pytest -q` (requires `python -m playwright install chromium` on fresh hosts).