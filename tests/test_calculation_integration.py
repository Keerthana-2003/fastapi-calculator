"""
Integration tests for Calculation model and persistence
"""
import pytest
from app.calculation_factory import CalculationFactory
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db, User, Calculation

# In-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestCalculationModelIntegration:
    """Test inserting and retrieving Calculation records"""

    def setup_method(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_insert_calculation_direct_db(self):
        # Create a user first
        db = TestingSessionLocal()
        user = User(username="alice", email="alice@example.com", password_hash="hash")
        db.add(user)
        db.commit()
        db.refresh(user)

        # Compute result using factory
        result = CalculationFactory.compute("add", 2, 3)

        # Create calculation record
        calc = Calculation(operation="add", operand_a=2.0, operand_b=3.0, result=result, user_id=user.id)
        db.add(calc)
        db.commit()
        db.refresh(calc)

        # Query back
        fetched = db.query(Calculation).filter(Calculation.id == calc.id).first()
        assert fetched is not None
        assert fetched.operation == "add"
        assert fetched.result == 5
        assert fetched.user_id == user.id
        db.close()

    def test_invalid_operation_in_factory(self):
        with pytest.raises(ValueError):
            CalculationFactory.compute("power", 2, 3)
