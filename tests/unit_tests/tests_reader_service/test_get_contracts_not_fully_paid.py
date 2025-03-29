import pytest
from models.contract import Contract, Base
from services.reader_service import get_contracts_not_fully_paid
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(engine)


def test_get_contracts_not_fully_paid_returns_not_fully_paid_contracts(db_session: Session):
    contract1 = Contract(total_amount=100.00, amount_left=50.00,
                         creation_date=datetime.strptime("2023-01-01", "%Y-%m-%d"),
                         status=True)
    contract2 = Contract(total_amount=200.00, amount_left=0.00,
                         creation_date=datetime.strptime("2023-01-01", "%Y-%m-%d"),
                         status=True)
    contract3 = Contract(total_amount=150.00, amount_left=150.00,
                         creation_date=datetime.strptime("2023-01-01", "%Y-%m-%d"),
                         status=False)

    db_session.add_all([contract1, contract2, contract3])
    db_session.commit()

    result = get_contracts_not_fully_paid(db_session)
    assert len(result) == 1
    assert contract1 in result
    assert contract3 not in result
    assert contract2 not in result


def test_get_contracts_not_fully_paid_returns_empty_if_all_fully_paid(db_session: Session):
    contract1 = Contract(total_amount=100.00, amount_left=0.00,
                         creation_date=datetime.strptime("2023-01-01", "%Y-%m-%d"),
                         status=True)
    contract2 = Contract(total_amount=200.00, amount_left=0.00,
                         creation_date=datetime.strptime("2023-01-01", "%Y-%m-%d"),
                         status=False)

    db_session.add_all([contract1, contract2])
    db_session.commit()

    result = get_contracts_not_fully_paid(db_session)
    assert len(result) == 0


def test_get_contracts_not_fully_paid_ignores_unsigned_contracts(db_session: Session):
    contract1 = Contract(total_amount=100.00, amount_left=50.00,
                         creation_date=datetime.strptime("2023-01-01", "%Y-%m-%d"),
                         status=True)
    contract2 = Contract(total_amount=150.00, amount_left=150.00,
                         creation_date=datetime.strptime("2023-01-01", "%Y-%m-%d"),
                         status=False)

    db_session.add_all([contract1, contract2])
    db_session.commit()

    result = get_contracts_not_fully_paid(db_session)
    assert len(result) == 1
    assert contract1 in result
    assert contract2 not in result
