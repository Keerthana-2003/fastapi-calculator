"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50, description="Username must be 3-50 characters")
    email: EmailStr = Field(..., description="Valid email address required")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username is alphanumeric with underscores/hyphens allowed"""
        if not all(c.isalnum() or c in ['_', '-'] for c in v):
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v


class UserRead(BaseModel):
    """Schema for returning user details (without password)"""
    id: int
    username: str
    email: str
    created_at: datetime

    # Pydantic v2 compatible configuration for ORM / SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class CalculationCreate(BaseModel):
    """Schema for creating a new calculation"""
    operation: str = Field(..., description="Operation type: add, subtract, multiply, divide")
    operand_a: float = Field(..., description="First operand")
    operand_b: float = Field(..., description="Second operand")

    @field_validator("operation")
    @classmethod
    def validate_operation(cls, v: str) -> str:
        """Validate operation is one of the allowed types"""
        allowed_operations = ["add", "subtract", "multiply", "divide"]
        if v.lower() not in allowed_operations:
            raise ValueError(f"Operation must be one of {allowed_operations}")
        return v.lower()

    @field_validator("operand_b")
    @classmethod
    def validate_divisor(cls, v: float, info) -> float:
        """Validate that operand_b is not zero for division"""
        if "operation" in info.data and info.data["operation"].lower() == "divide" and v == 0:
            raise ValueError("Cannot divide by zero")
        return v


class CalculationRead(BaseModel):
    """Schema for returning calculation details"""
    id: int
    operation: str
    operand_a: float
    operand_b: float
    result: float
    timestamp: datetime
    user_id: int

    # Pydantic v2 compatible configuration for ORM / SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
