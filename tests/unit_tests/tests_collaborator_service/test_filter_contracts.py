import pytest
from unittest.mock import MagicMock
from models.contract import Contract
from models.client import Client
from models.collaborator import Collaborator
from services.contract_service import filter_contracts


@pytest.fixture
def db_session():
    return MagicMock()

@pytest.fixture
def commercial_user():
    return Collaborator(id=1, email="commercial@example.com")

@pytest.fixture
def gestion_payload():
    return {"role": "gestion", "sub": "admin@example.com"}

@pytest.fixture
def commercial_payload():
    return {"role": "commercial", "sub": "commercial@example.com"}

@pytest.fixture
def sample_contracts():
    return [
        Contract(id=1, status=False, amount_left=0),   # non signé
        Contract(id=2, status=True, amount_left=1000), # non payé
        Contract(id=3, status=True, amount_left=0),    # payé & signé
    ]


def test_gestion_filters_unsigned_contracts(db_session, gestion_payload, sample_contracts):
    mock_query_user = MagicMock()
    mock_query_user.filter_by.return_value.first.return_value = Collaborator(email="admin@example.com")

    mock_query_contracts = MagicMock()
    mock_query_contracts.filter.return_value.all.return_value = [sample_contracts[0]]

    db_session.query.side_effect = [mock_query_user, mock_query_contracts]

    result = filter_contracts(db_session, gestion_payload, filter_by="unsigned")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id == 1
    assert result[0].status is False

def test_gestion_filters_unpaid_contracts(db_session, gestion_payload, sample_contracts):
    # Mock collaborator
    mock_query_user = MagicMock()
    mock_query_user.filter_by.return_value.first.return_value = Collaborator(email="admin@example.com")

    # Mock contract
    mock_query_contracts = MagicMock()
    mock_query_contracts.filter.return_value.all.return_value = [sample_contracts[1]]

    db_session.query.side_effect = [mock_query_user, mock_query_contracts]

    result = filter_contracts(db_session, gestion_payload, filter_by="unpaid")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id == 2
    assert result[0].amount_left > 0

def test_commercial_filters_unpaid_contracts_of_their_clients(db_session, commercial_payload, commercial_user):
    contract = Contract(id=5, status=True, amount_left=200)
    client = Client(id=1, commercial_id=commercial_user.id)
    contract.client = client

    mock_query_user = MagicMock()
    mock_query_user.filter_by.return_value.first.return_value = commercial_user

    mock_query_contracts = MagicMock()
    mock_after_filter = mock_query_contracts.filter.return_value
    mock_after_join = mock_after_filter.join.return_value
    mock_after_second_filter = mock_after_join.filter.return_value
    mock_after_second_filter.all.return_value = [contract]

    db_session.query.side_effect = [mock_query_user, mock_query_contracts]

    result = filter_contracts(db_session, commercial_payload, filter_by="unpaid")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id == 5
    assert result[0].client.commercial_id == commercial_user.id

def test_unauthorized_role_cannot_filter_contracts(db_session):
    payload = {"role": "support", "sub": "support@example.com"}

    result = filter_contracts(db_session, payload, filter_by="unpaid")

    assert isinstance(result, list)
    assert result == []

def test_unknown_user_returns_empty_list(db_session):
    mock_query_user = MagicMock()
    mock_query_user.filter_by.return_value.first.return_value = None

    db_session.query.side_effect = [mock_query_user]

    payload = {"role": "commercial", "sub": "ghost@example.com"}
    result = filter_contracts(db_session, payload, filter_by="unsigned")

    assert isinstance(result, list)
    assert result == []