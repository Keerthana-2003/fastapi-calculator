"""
Unit and integration tests for calculation factory and Calculation model persistence
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, Calculation, User
from app.calculation_factory import CalculationFactory


def test_factory_operations():
    assert CalculationFactory.compute("add", 2, 3) == 5
    assert CalculationFactory.compute("subtract", 5, 3) == 2
    assert CalculationFactory.compute("multiply", 4, 5) == 20
    assert CalculationFactory.compute("divide", 10, 2) == 5

    with pytest.raises(ValueError):
        CalculationFactory.compute("power", 2, 3)


# Integration: persist a calculation in an in-memory SQLite DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module(module):
    Base.metadata.create_all(bind=engine)


def teardown_module(module):
    Base.metadata.drop_all(bind=engine)


def test_persist_calculation():
    # create user and calculation in same session
    db = TestingSessionLocal()
    try:
        user = User(username="tester", email="tester@example.com", password_hash="x")
        db.add(user)
        db.commit()
        db.refresh(user)

        # compute result
        result = CalculationFactory.compute("multiply", 3.5, 2)

        calc = Calculation(
            operation="multiply",
            operand_a=3.5,
            operand_b=2,
            result=result,
            user_id=user.id
        )
        db.add(calc)
        db.commit()
        db.refresh(calc)

        # verify persisted values
        assert calc.id is not None
        assert abs(calc.result - 7.0) < 1e-9
        assert calc.user_id == user.id

    finally:
        db.close()
