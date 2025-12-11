# FastAPI Calculator — Module 12 Submission

## Overview

This document is the submission write-up for Module 12: User & Calculation Routes (BREAD) with integration testing and CI/CD.

- Submission branch: `module-12-submission`
- Branch URL for grading: https://github.com/Keerthana-2003/fastapi-calculator/tree/module-12-submission

## What I implemented

- User endpoints: `POST /users/register`, `POST /users/login`, `GET /users/{id}` with secure password hashing.
- Calculation BREAD endpoints: `POST /calculations`, `GET /calculations`, `GET /calculations/{id}`, `PUT /calculations/{id}`, `DELETE /calculations/{id}`. All endpoints enforce user isolation via the `user_id` query parameter.
- Calculation results are computed server-side using `CalculationFactory.compute()` and persisted in the `calculations` table.
- Comprehensive integration tests covering user flows and calculation BREAD operations were added.

## Tests and CI

- Local test run on this branch: `pytest tests/ --ignore=tests/test_e2e.py` → **70 passed** (verified locally).
- GitHub Actions workflow included with this repo spins up PostgreSQL and runs the same test suite as part of CI.
- On successful CI runs the workflow can build and push a Docker image to Docker Hub (replace the placeholder repo in the README with your Docker Hub repo if required).

### Test coverage (high level)

- User registration/login and DB checks
- Calculation BREAD: create, browse, read, update, delete; validation and error handling (404/422/400)
- Schema validation and operation unit tests

## How to verify (Codespaces)

1. Open Codespaces and checkout: `git checkout module-12-submission`
2. Start services: `docker-compose up --build`
3. Open Swagger UI: `http://localhost:8000/docs`
4. Register a user, create calculations, and exercise the BREAD endpoints.
5. Run tests: `pytest tests/ --ignore=tests/test_e2e.py -q` (should show 70 passed locally)

## Screenshots (attach to this document before submission)

Provide the following screenshots in `docs/screenshots/` and reference them in this document before final submission:

- `1_register_user.png` — successful user registration (response)
- `2_create_calculation.png` — POST /calculations response showing computed `result`
- `3_browse_calculations.png` — GET /calculations list
- `4_read_calculation.png` — GET /calculations/{id}
- `5_update_calculation.png` — PUT showing updated `result`
- `6_delete_calculation.png` — DELETE confirmation or 204
- `7_ci_tests_pass.png` — GitHub Actions run showing successful tests

Add images with standard markdown, e.g.:

`![Tests passed](docs/screenshots/7_ci_tests_pass.png)`

## Reflection (brief)

I implemented the BREAD calculation endpoints and integrated them with the existing SQLAlchemy models and Pydantic schemas. Key challenges were ensuring correct error propagation (preserving `HTTPException` status codes) and maintaining test isolation across multiple integration tests. I resolved these by re-raising `HTTPException` in endpoint handlers and consolidating calculation BREAD tests into the integration test module that uses the same fixtures for database setup/teardown.

## Files for grading

- `app/` — application code (endpoints, models, schemas)
- `tests/` — integration and unit tests (70 passing on this branch)
- `.github/workflows/python-app.yml` — CI workflow
- `DOCUMENTATION.md` — this submission write-up
- `README.md` — repo-level instructions

## Notes

- Do NOT include private notes or personal `submissionguide.md` files in the public branch used for submission. I keep any personal guides outside the public history and did not include them in this branch tip.
- Replace the Docker Hub placeholder in the README with your actual Docker Hub repository if you want CI to push images.

---

When your screenshots are ready in `docs/screenshots/` I can insert them into this document and commit the updated document.
