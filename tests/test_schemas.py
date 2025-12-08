"""
Unit tests for Pydantic schemas validation
"""
import pytest
from pydantic import ValidationError
from app.schemas import UserCreate, UserLogin, CalculationCreate


class TestUserCreateSchema:
    """Test suite for UserCreate schema validation"""

    def test_valid_user_creation(self):
        """Test creating a user with valid data"""
        user = UserCreate(
            username="john_doe",
            email="john@example.com",
            password="secure_password_123"
        )
        assert user.username == "john_doe"
        assert user.email == "john@example.com"
        assert user.password == "secure_password_123"

    def test_username_too_short(self):
        """Test that username must be at least 3 characters"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab",
                email="test@example.com",
                password="password123"
            )
        assert "at least 3 characters" in str(exc_info.value)

    def test_username_too_long(self):
        """Test that username must not exceed 50 characters"""
        with pytest.raises(ValidationError):
            UserCreate(
                username="a" * 51,
                email="test@example.com",
                password="password123"
            )

    def test_username_with_invalid_characters(self):
        """Test that username only allows alphanumeric, underscore, and hyphen"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john@doe!",
                email="test@example.com",
                password="password123"
            )
        assert "alphanumeric" in str(exc_info.value)

    def test_username_with_valid_special_characters(self):
        """Test that username allows underscore and hyphen"""
        user = UserCreate(
            username="john_doe-123",
            email="test@example.com",
            password="password123"
        )
        assert user.username == "john_doe-123"

    def test_invalid_email(self):
        """Test that email must be valid format"""
        with pytest.raises(ValidationError):
            UserCreate(
                username="john_doe",
                email="invalid-email",
                password="password123"
            )

    def test_password_too_short(self):
        """Test that password must be at least 6 characters"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="john@example.com",
                password="pass"
            )
        assert "at least 6 characters" in str(exc_info.value)

    def test_valid_password_with_special_characters(self):
        """Test password with special characters"""
        user = UserCreate(
            username="john_doe",
            email="john@example.com",
            password="P@ss!word#123"
        )
        assert user.password == "P@ss!word#123"


class TestUserLoginSchema:
    """Test suite for UserLogin schema validation"""

    def test_valid_login(self):
        """Test valid login credentials"""
        login = UserLogin(
            email="user@example.com",
            password="password123"
        )
        assert login.email == "user@example.com"
        assert login.password == "password123"

    def test_invalid_email_format(self):
        """Test that email must be valid format"""
        with pytest.raises(ValidationError):
            UserLogin(
                email="invalid-email",
                password="password123"
            )


class TestCalculationCreateSchema:
    """Test suite for CalculationCreate schema validation"""

    def test_valid_addition(self):
        """Test valid addition operation"""
        calc = CalculationCreate(
            operation="add",
            operand_a=5.0,
            operand_b=3.0
        )
        assert calc.operation == "add"
        assert calc.operand_a == 5.0
        assert calc.operand_b == 3.0

    def test_valid_subtraction(self):
        """Test valid subtraction operation"""
        calc = CalculationCreate(
            operation="subtract",
            operand_a=10.0,
            operand_b=3.0
        )
        assert calc.operation == "subtract"

    def test_valid_multiplication(self):
        """Test valid multiplication operation"""
        calc = CalculationCreate(
            operation="multiply",
            operand_a=4.0,
            operand_b=5.0
        )
        assert calc.operation == "multiply"

    def test_valid_division(self):
        """Test valid division operation"""
        calc = CalculationCreate(
            operation="divide",
            operand_a=10.0,
            operand_b=2.0
        )
        assert calc.operation == "divide"

    def test_invalid_operation(self):
        """Test that invalid operation raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(
                operation="power",
                operand_a=5.0,
                operand_b=2.0
            )
        assert "Operation must be one of" in str(exc_info.value)

    def test_division_by_zero(self):
        """Test that division by zero raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(
                operation="divide",
                operand_a=10.0,
                operand_b=0.0
            )
        assert "Cannot divide by zero" in str(exc_info.value)

    def test_operation_case_insensitive(self):
        """Test that operation is converted to lowercase"""
        calc = CalculationCreate(
            operation="ADD",
            operand_a=5.0,
            operand_b=3.0
        )
        assert calc.operation == "add"

    def test_negative_operands(self):
        """Test that negative operands are allowed"""
        calc = CalculationCreate(
            operation="add",
            operand_a=-5.0,
            operand_b=-3.0
        )
        assert calc.operand_a == -5.0
        assert calc.operand_b == -3.0
