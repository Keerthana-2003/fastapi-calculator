"""
Integration tests for user registration and login endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override get_db dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create TestClient
client = TestClient(app)


class TestUserRegistration:
    """Integration tests for user registration endpoint"""

    def setup_method(self):
        """Setup before each test - clear database"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_register_user_success(self):
        """Test successful user registration"""
        response = client.post(
            "/users/register",
            json={
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secure_password_123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "john_doe"
        assert data["email"] == "john@example.com"
        assert "password_hash" not in data  # Password should not be in response
        assert "id" in data
        assert "created_at" in data

    def test_register_user_invalid_email(self):
        """Test registration with invalid email format"""
        response = client.post(
            "/users/register",
            json={
                "username": "john_doe",
                "email": "invalid-email",
                "password": "secure_password_123"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_register_user_short_password(self):
        """Test registration with password too short"""
        response = client.post(
            "/users/register",
            json={
                "username": "john_doe",
                "email": "john@example.com",
                "password": "short"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_register_user_short_username(self):
        """Test registration with username too short"""
        response = client.post(
            "/users/register",
            json={
                "username": "ab",
                "email": "john@example.com",
                "password": "secure_password"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_register_user_duplicate_username(self):
        """Test registration with duplicate username"""
        # Register first user
        client.post(
            "/users/register",
            json={
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secure_password_123"
            }
        )

        # Try to register with same username
        response = client.post(
            "/users/register",
            json={
                "username": "john_doe",
                "email": "different@example.com",
                "password": "secure_password_123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_user_duplicate_email(self):
        """Test registration with duplicate email"""
        # Register first user
        client.post(
            "/users/register",
            json={
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secure_password_123"
            }
        )

        # Try to register with same email
        response = client.post(
            "/users/register",
            json={
                "username": "jane_doe",
                "email": "john@example.com",
                "password": "secure_password_123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_user_invalid_username_characters(self):
        """Test registration with invalid username characters"""
        response = client.post(
            "/users/register",
            json={
                "username": "john@doe!",
                "email": "john@example.com",
                "password": "secure_password_123"
            }
        )
        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Integration tests for user login endpoint"""

    def setup_method(self):
        """Setup before each test - clear database and create test user"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        # Create a test user
        client.post(
            "/users/register",
            json={
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secure_password_123"
            }
        )

    def test_login_user_success(self):
        """Test successful user login"""
        response = client.post(
            "/users/login",
            json={
                "email": "john@example.com",
                "password": "secure_password_123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert data["user"]["username"] == "john_doe"
        assert data["user"]["email"] == "john@example.com"

    def test_login_user_invalid_email(self):
        """Test login with non-existent email"""
        response = client.post(
            "/users/login",
            json={
                "email": "nonexistent@example.com",
                "password": "secure_password_123"
            }
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_user_wrong_password(self):
        """Test login with incorrect password"""
        response = client.post(
            "/users/login",
            json={
                "email": "john@example.com",
                "password": "wrong_password"
            }
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_user_case_sensitive_password(self):
        """Test that password is case-sensitive"""
        response = client.post(
            "/users/login",
            json={
                "email": "john@example.com",
                "password": "SECURE_PASSWORD_123"
            }
        )
        assert response.status_code == 401

    def test_login_user_invalid_email_format(self):
        """Test login with invalid email format"""
        response = client.post(
            "/users/login",
            json={
                "email": "invalid-email",
                "password": "secure_password_123"
            }
        )
        assert response.status_code == 422  # Validation error


class TestGetUser:
    """Integration tests for get user endpoint"""

    def setup_method(self):
        """Setup before each test - clear database and create test user"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        # Create a test user
        client.post(
            "/users/register",
            json={
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secure_password_123"
            }
        )

    def test_get_user_success(self):
        """Test retrieving user by ID"""
        response = client.get("/users/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["username"] == "john_doe"
        assert data["email"] == "john@example.com"

    def test_get_user_not_found(self):
        """Test retrieving non-existent user"""
        response = client.get("/users/999")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]


class TestCalculatorEndpoints:
    """Test that calculator endpoints still work"""

    def test_add_endpoint(self):
        """Test add calculator endpoint"""
        response = client.get("/add?a=2&b=3")
        assert response.status_code == 200
        assert response.json() == {"result": 5}

    def test_subtract_endpoint(self):
        """Test subtract calculator endpoint"""
        response = client.get("/subtract?a=5&b=3")
        assert response.status_code == 200
        assert response.json() == {"result": 2}

    def test_multiply_endpoint(self):
        """Test multiply calculator endpoint"""
        response = client.get("/multiply?a=2&b=3")
        assert response.status_code == 200
        assert response.json() == {"result": 6}

    def test_divide_endpoint(self):
        """Test divide calculator endpoint"""
        response = client.get("/divide?a=6&b=3")
        assert response.status_code == 200
        assert response.json() == {"result": 2}

    def test_divide_by_zero_endpoint(self):
        """Test divide by zero error"""
        response = client.get("/divide?a=5&b=0")
        assert response.status_code == 400
        assert "Cannot divide by zero" in response.json()["detail"]
