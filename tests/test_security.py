"""
Unit tests for password hashing and security
"""
import pytest
from app.security import hash_password, verify_password


class TestPasswordHashing:
    """Test suite for password hashing functions"""

    def test_hash_password_creates_different_hashes(self):
        """Test that hashing the same password twice produces different hashes (due to salt)"""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2

    def test_verify_password_with_correct_password(self):
        """Test that verify_password returns True with correct password"""
        password = "correct_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_with_incorrect_password(self):
        """Test that verify_password returns False with incorrect password"""
        correct_password = "correct_password_123"
        wrong_password = "wrong_password_123"
        hashed = hash_password(correct_password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_is_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        # Different case should not verify
        assert verify_password("testpassword123", hashed) is False

    def test_hash_password_length(self):
        """Test that hashed password is a reasonable length"""
        password = "test_password"
        hashed = hash_password(password)
        
        # Bcrypt hashes are typically 60 characters
        assert len(hashed) >= 50
        assert len(hashed) <= 100

    def test_hash_password_with_special_characters(self):
        """Test hashing passwords with special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_hash_password_with_unicode_characters(self):
        """Test hashing passwords with unicode characters"""
        password = "Pässwörd123日本語"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
