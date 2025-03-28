# File: tests/test_reader_service.py

import pytest
from models.contract import Contract, Base
from services.reader_service import get_contracts_not_signed
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create a database fixture for pytest
@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:")  # Use in-memory SQLite DB for testing
    Base.metadata.create_all(bind=engine)  # Create tables
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db  # Provide the database session to a test function
    finally:
        db.rollback()  # Rollback any changes made during the test
        db.close()  # Close the session
        Base.metadata.drop_all(bind=engine)  # Drop tables


def test_get_contracts_not_signed_returns_unsigned_contracts(test_db):
    # Arrange
    unsigned_contract1 = Contract(total_amount=1000, amount_left=500,
                                  creation_date=datetime.strptime("2023-01-01", "%Y-%m-%d"),
                                  status=False)
    unsigned_contract2 = Contract(total_amount=2000, amount_left=1500,
                                  creation_date=datetime.strptime("2023-02-01", "%Y-%m-%d"),
                                  status=False)
    signed_contract = Contract(total_amount=1500, amount_left=750,
                               creation_date=datetime.strptime("2023-03-01", "%Y-%m-%d"),
                               status=True)
    test_db.add_all([unsigned_contract1, unsigned_contract2, signed_contract])
    test_db.commit()

    # Act
    result = get_contracts_not_signed(test_db)

    # Assert
    assert len(result) == 2
    assert unsigned_contract1 in result
    assert unsigned_contract2 in result
    assert signed_contract not in result


def test_get_contracts_not_signed_with_no_contracts_in_db(test_db):
    # Act
    result = get_contracts_not_signed(test_db)

    # Assert
    assert result == []


def test_get_contracts_not_signed_with_only_signed_contracts(test_db):
    # Arrange
    signed_contract1 = Contract(total_amount=1200, amount_left=600,
                                creation_date=datetime.strptime("2023-04-01", "%Y-%m-%d"),
                                status=True)
    signed_contract2 = Contract(total_amount=2500, amount_left=1250,
                                creation_date=datetime.strptime("2023-05-01", "%Y-%m-%d"),
                                status=True)
    test_db.add_all([signed_contract1, signed_contract2])
    test_db.commit()

    # Act
    result = get_contracts_not_signed(test_db)

    # Assert
    assert result == []


def test_get_contracts_not_signed_with_mixed_signed_and_unsigned_contracts(test_db):
    # Arrange
    unsigned_contract = Contract(total_amount=1800, amount_left=900,
                                 creation_date=datetime.strptime("2023-06-01", "%Y-%m-%d"),
                                 status=False)
    signed_contract = Contract(total_amount=3000, amount_left=1200,
                               creation_date=datetime.strptime("2023-07-01", "%Y-%m-%d"),
                               status=True)
    test_db.add_all([unsigned_contract, signed_contract])
    test_db.commit()

    # Act
    result = get_contracts_not_signed(test_db)

    # Assert
    assert len(result) == 1
    assert unsigned_contract in result
    assert signed_contract not in result
