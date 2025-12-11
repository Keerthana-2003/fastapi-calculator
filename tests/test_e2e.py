import os
import subprocess
import time
import uuid

import pytest
import requests
from playwright.sync_api import sync_playwright

API_BASE = "http://127.0.0.1:8000"
REGISTER_PAGE = f"{API_BASE}/register.html"
LOGIN_PAGE = f"{API_BASE}/login.html"
CALC_PAGE = f"{API_BASE}/calculations.html"


@pytest.fixture(scope="session")
def server():
    """Ensure the FastAPI server is reachable; start a local one if needed."""
    try:
        requests.get(API_BASE, timeout=1)
        yield
        return
    except Exception:
        pass

    proc = subprocess.Popen([
        "python",
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ])

    for _ in range(60):
        try:
            requests.get(API_BASE, timeout=1)
            break
        except Exception:
            time.sleep(1)
    else:  # pragma: no cover - defensive
        proc.terminate()
        raise RuntimeError("Server did not start in time")

    yield
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


def _unique_email() -> str:
    return f"user_{uuid.uuid4().hex[:8]}@example.com"


def _api_register(email: str, password: str, username: str | None = None):
    payload = {
        "username": username or f"user_{uuid.uuid4().hex[:6]}",
        "email": email,
        "password": password,
    }
    resp = requests.post(f"{API_BASE}/register", json=payload, timeout=5)
    assert resp.status_code in (200, 201)
    return resp.json()


def _api_create_calc(token: str, operation: str = "add", a: float = 2.0, b: float = 3.0):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(
        f"{API_BASE}/calculations",
        json={"operation": operation, "operand_a": a, "operand_b": b},
        headers=headers,
        timeout=5,
    )
    assert resp.status_code == 201
    return resp.json()


def test_register_positive(server, browser):
    page = browser.new_page()
    page.goto(REGISTER_PAGE)

    email = _unique_email()
    username = f"u_{uuid.uuid4().hex[:5]}"
    password = "supersecret"

    page.fill("#username", username)
    page.fill("#email", email)
    page.fill("#password", password)
    page.fill("#confirm", password)
    page.click("#submit")

    page.wait_for_timeout(500)
    status_text = page.text_content("#status") or ""
    assert "Registration successful" in status_text


def test_login_positive(server, browser):
    email = _unique_email()
    password = "mystrongpass"
    _api_register(email=email, password=password)

    page = browser.new_page()
    page.goto(LOGIN_PAGE)
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("#submit")

    page.wait_for_timeout(500)
    status_text = page.text_content("#status") or ""
    assert "Login successful" in status_text
    token = page.evaluate("() => localStorage.getItem('access_token')")
    assert token is not None


def test_register_short_password_client_validation(server, browser):
    page = browser.new_page()
    page.goto(REGISTER_PAGE)

    email = _unique_email()
    page.fill("#username", "shorty")
    page.fill("#email", email)
    page.fill("#password", "123")
    page.fill("#confirm", "123")
    page.click("#submit")

    page.wait_for_timeout(400)
    status_text = (page.text_content("#status") or "").lower()
    assert "password" in status_text


def test_login_wrong_password(server, browser):
    email = _unique_email()
    _api_register(email=email, password="correctpass")

    page = browser.new_page()
    page.goto(LOGIN_PAGE)
    page.fill("#email", email)
    page.fill("#password", "wrongpass")
    page.click("#submit")

    page.wait_for_timeout(500)
    status_text = page.text_content("#status") or ""
    assert "Invalid" in status_text


def test_calculations_create_and_browse(server, browser):
    # Register and get token via API for speed
    email = _unique_email()
    password = "calcpass123"
    reg = _api_register(email=email, password=password)
    token = reg["access_token"]

    page = browser.new_page()
    page.goto(CALC_PAGE)
    page.evaluate("(t) => localStorage.setItem('access_token', t)", token)

    page.select_option("#op", "add")
    page.fill("#a", "4")
    page.fill("#b", "5")
    page.click("#create-btn")
    page.wait_for_timeout(600)

    status_text = page.text_content("#status") or ""
    assert ("Created calculation" in status_text) or ("Loaded calculations" in status_text)
    list_text = page.text_content("#calc-list") or ""
    assert "add(4" in list_text


def test_calculations_update_and_delete(server, browser):
    email = _unique_email()
    password = "calcpass456"
    reg = _api_register(email=email, password=password)
    token = reg["access_token"]

    created = _api_create_calc(token, operation="subtract", a=10, b=4)
    calc_id = created["id"]

    page = browser.new_page()
    page.goto(CALC_PAGE)
    page.evaluate("(t) => localStorage.setItem('access_token', t)", token)

    page.fill("#edit-id", str(calc_id))
    page.select_option("#edit-op", "multiply")
    page.fill("#edit-a", "3")
    page.fill("#edit-b", "3")
    page.click("#update-btn")
    page.wait_for_timeout(600)
    status_text = page.text_content("#status") or ""
    assert ("Updated" in status_text) or ("Loaded calculations" in status_text)
    list_text = page.text_content("#calc-list") or ""
    assert "multiply(3" in list_text

    page.fill("#delete-id", str(calc_id))
    page.click("#delete-btn")
    page.wait_for_timeout(400)
    status_text = page.text_content("#status") or ""
    assert ("Deleted" in status_text) or ("Loaded calculations" in status_text)
    list_text = page.text_content("#calc-list") or ""
    assert f"ID {calc_id}" not in list_text


def test_calculations_missing_token_negative(server, browser):
    page = browser.new_page()
    page.goto(CALC_PAGE)
    page.evaluate("() => localStorage.removeItem('access_token')")
    page.click("#refresh-btn")
    page.wait_for_timeout(300)
    status_text = page.text_content("#status") or ""
    assert "Missing token" in status_text


def test_calculations_invalid_operand_negative(server, browser):
    email = _unique_email()
    password = "calcpass789"
    reg = _api_register(email=email, password=password)
    token = reg["access_token"]

    page = browser.new_page()
    page.goto(CALC_PAGE)
    page.evaluate("(t) => localStorage.setItem('access_token', t)", token)

    page.select_option("#op", "add")
    page.evaluate("() => { document.getElementById('a').value = 'abc'; }")
    page.fill("#b", "5")
    page.click("#create-btn")
    page.wait_for_timeout(400)
    status_text = page.text_content("#status") or ""
    assert "Operands" in status_text
