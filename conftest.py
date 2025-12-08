"""
Pytest configuration file
"""
import pytest


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "e2e: marks tests as e2e (deselect with '-m \"not e2e\"')"
    )
