"""
Password hashing and security utilities
"""
from passlib.context import CryptContext

# Create password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    
    Args:
        password: Plain-text password to hash
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain-text password matches a hashed password.
    
    Args:
        plain_password: Plain-text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)
