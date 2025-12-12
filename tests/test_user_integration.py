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


class TestProfileEndpoints:
    """Integration tests for profile and password endpoints"""

    def setup_method(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        reg = client.post(
            "/register",
            json={"username": "owner", "email": "owner@example.com", "password": "changeme123"},
        )
        assert reg.status_code == 201
        self.token = reg.json()["access_token"]

    def _auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def test_get_me_success(self):
        resp = client.get("/me", headers=self._auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "owner@example.com"
        assert data["username"] == "owner"

    def test_update_profile_success(self):
        resp = client.put(
            "/me",
            headers={"Content-Type": "application/json", **self._auth_headers()},
            json={"username": "owner2", "email": "owner2@example.com"},
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["user"]["username"] == "owner2"
        assert payload["user"]["email"] == "owner2@example.com"
        assert payload["access_token"]

    def test_update_profile_duplicate_email(self):
        client.post(
            "/register",
            json={"username": "other", "email": "taken@example.com", "password": "changeme123"},
        )

        resp = client.put(
            "/me",
            headers={"Content-Type": "application/json", **self._auth_headers()},
            json={"email": "taken@example.com"},
        )
        assert resp.status_code == 400
        assert "Email already taken" in resp.json()["detail"]

    def test_update_profile_missing_fields(self):
        resp = client.put(
            "/me",
            headers={"Content-Type": "application/json", **self._auth_headers()},
            json={},
        )
        assert resp.status_code == 400

    def test_change_password_success(self):
        resp = client.post(
            "/me/password",
            headers={"Content-Type": "application/json", **self._auth_headers()},
            json={
                "current_password": "changeme123",
                "new_password": "newsecret456",
                "confirm_new_password": "newsecret456",
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["access_token"]

        bad_login = client.post(
            "/users/login",
            json={"email": "owner@example.com", "password": "changeme123"},
        )
        assert bad_login.status_code == 401

        good_login = client.post(
            "/users/login",
            json={"email": "owner@example.com", "password": "newsecret456"},
        )
        assert good_login.status_code == 200


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


class TestCalculationBREAD:
    """Integration tests for calculation BREAD endpoints"""

    def setup_method(self):
        """Clear database and create test user before each test"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        # Create a test user
        client.post(
            "/users/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "secure_password"
            }
        )
        self.user_id = 1

    def test_add_calculation_success(self):
        """Test creating a new calculation"""
        response = client.post(
            "/calculations",
            params={"user_id": self.user_id},
            json={"operation": "add", "operand_a": 5.0, "operand_b": 3.0}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["operation"] == "add"
        assert data["result"] == 8.0
        assert data["user_id"] == self.user_id

    def test_add_calculation_subtract(self):
        """Test creating a subtraction calculation"""
        response = client.post(
            "/calculations",
            params={"user_id": self.user_id},
            json={"operation": "subtract", "operand_a": 10.0, "operand_b": 3.0}
        )
        assert response.status_code == 201
        assert response.json()["result"] == 7.0

    def test_add_calculation_invalid_operation(self):
        """Test with invalid operation type"""
        response = client.post(
            "/calculations",
            params={"user_id": self.user_id},
            json={"operation": "power", "operand_a": 2.0, "operand_b": 3.0}
        )
        assert response.status_code == 422

    def test_add_calculation_nonexistent_user(self):
        """Test creating calculation for non-existent user"""
        response = client.post(
            "/calculations",
            params={"user_id": 999},
            json={"operation": "add", "operand_a": 2.0, "operand_b": 3.0}
        )
        assert response.status_code == 404

    def test_browse_calculations_empty(self):
        """Test browsing calculations when none exist"""
        response = client.get("/calculations", params={"user_id": self.user_id})
        assert response.status_code == 200
        assert response.json() == []

    def test_browse_calculations_multiple(self):
        """Test browsing multiple calculations"""
        # Create 2 calculations
        for op, a, b in [("add", 2, 3), ("multiply", 4, 5)]:
            client.post(
                "/calculations",
                params={"user_id": self.user_id},
                json={"operation": op, "operand_a": a, "operand_b": b}
            )
        
        response = client.get("/calculations", params={"user_id": self.user_id})
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_read_calculation_success(self):
        """Test retrieving a single calculation"""
        # Create a calculation
        post_response = client.post(
            "/calculations",
            params={"user_id": self.user_id},
            json={"operation": "multiply", "operand_a": 3.0, "operand_b": 4.0}
        )
        calc_id = post_response.json()["id"]
        
        # Read it back
        response = client.get(f"/calculations/{calc_id}", params={"user_id": self.user_id})
        assert response.status_code == 200
        assert response.json()["result"] == 12.0

    def test_read_calculation_not_found(self):
        """Test reading non-existent calculation"""
        response = client.get("/calculations/999", params={"user_id": self.user_id})
        assert response.status_code == 404

    def test_edit_calculation_success(self):
        """Test updating a calculation"""
        # Create calculation
        post_response = client.post(
            "/calculations",
            params={"user_id": self.user_id},
            json={"operation": "add", "operand_a": 2.0, "operand_b": 3.0}
        )
        calc_id = post_response.json()["id"]
        
        # Update it
        response = client.put(
            f"/calculations/{calc_id}",
            params={"user_id": self.user_id},
            json={"operation": "multiply", "operand_a": 4.0, "operand_b": 5.0}
        )
        assert response.status_code == 200
        assert response.json()["result"] == 20.0

    def test_edit_calculation_not_found(self):
        """Test updating non-existent calculation"""
        response = client.put(
            "/calculations/999",
            params={"user_id": self.user_id},
            json={"operation": "add", "operand_a": 1.0, "operand_b": 1.0}
        )
        assert response.status_code == 404

    def test_delete_calculation_success(self):
        """Test deleting a calculation"""
        # Create calculation
        post_response = client.post(
            "/calculations",
            params={"user_id": self.user_id},
            json={"operation": "add", "operand_a": 2.0, "operand_b": 3.0}
        )
        calc_id = post_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/calculations/{calc_id}", params={"user_id": self.user_id})
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = client.get(f"/calculations/{calc_id}", params={"user_id": self.user_id})
        assert get_response.status_code == 404

    def test_delete_calculation_not_found(self):
        """Test deleting non-existent calculation"""
        response = client.delete("/calculations/999", params={"user_id": self.user_id})
        assert response.status_code == 404

