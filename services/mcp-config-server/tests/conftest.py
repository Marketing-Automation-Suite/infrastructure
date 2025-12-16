"""
Pytest configuration and fixtures
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment variables
os.environ["ENCRYPTION_KEY"] = "test_encryption_key_for_testing_only_do_not_use_in_production"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"


@pytest.fixture
def test_db():
    """Create a test database session"""
    # In a real test setup, you'd use a test database
    # For now, this is a placeholder
    pass

