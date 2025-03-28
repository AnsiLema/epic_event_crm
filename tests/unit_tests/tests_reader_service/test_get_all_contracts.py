from unittest.mock import MagicMock
import pytest
from models.contract import Contract
from services.reader_service import get_all_contracts
from sqlalchemy.orm import Session
from datetime import datetime


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


def test_get_all_contracts_empty_db(mock_session):
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.all.return_value = []

    result = get_all_contracts(mock_session)
    assert result == []

    mock_session.query.assert_called_once_with(Contract)
    mock_query.all.assert_called_once()


def test_get_all_contracts_with_contracts(mock_session):
    contract_1 = Contract(id=1, total_amount=1000, amount_left=500,
                          creation_date=datetime.strptime("2023-01-01", "%Y-%m-%d").date(), status=True)
    contract_2 = Contract(id=2, total_amount=2000, amount_left=1500,
                          creation_date=datetime.strptime("2023-02-01", "%Y-%m-%d").date(), status=False)

    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.all.return_value = [contract_1, contract_2]

    result = get_all_contracts(mock_session)
    assert result == [contract_1, contract_2]

    mock_session.query.assert_called_once_with(Contract)
    mock_query.all.assert_called_once()


def test_get_all_contracts_database_error(mock_session):
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.all.side_effect = Exception("Database error")

    with pytest.raises(Exception, match="Database error"):
        get_all_contracts(mock_session)

    mock_session.query.assert_called_once_with(Contract)
    mock_query.all.assert_called_once()
