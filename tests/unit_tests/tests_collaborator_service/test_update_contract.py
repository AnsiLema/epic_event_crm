from unittest.mock import MagicMock

import pytest
from models.client import Client
from models.collaborator import Collaborator
from models.contract import Contract
from services.contract_service import update_contract
from models.role import Role


@pytest.fixture
def db_session():
    return MagicMock()


@pytest.fixture
def mock_contract():
    return Contract(
        id=1,
        total_amount=1000.0,
        amount_left=500.0,
        status=False
    )


@pytest.fixture
def mock_client():
    return Client(id=2, name="Mock Client")


@pytest.fixture
def mock_commercial():
    role = Role(name="commercial")
    return Collaborator(id=3, name="Mock Commercial", email="commercial@test.com", role=role)


@pytest.fixture
def mock_user_payload():
    return {"sub": "user@example.com", "role": "gestion"}


def test_update_contract_successful_update(db_session, mock_contract, mock_user_payload):
    db_session.query().filter_by().first.side_effect = [
        mock_contract,
        Collaborator(id=1, email="user@example.com")
    ]
    db_session.commit = MagicMock()
    db_session.refresh = MagicMock()

    updated_contract = update_contract(
        db_session, mock_user_payload, 1, new_total_amount=1500.0
    )

    assert updated_contract is not None
    assert updated_contract.total_amount == 1500.0
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(mock_contract)


def test_update_contract_contract_not_found(db_session, mock_user_payload):
    db_session.query().filter_by().first.return_value = None

    result = update_contract(db_session, mock_user_payload, 999)

    assert result is None
    db_session.commit.assert_not_called()


def test_update_contract_user_not_found(db_session, mock_contract):
    db_session.query().filter_by().first.side_effect = [
        mock_contract,
        None
    ]

    result = update_contract(db_session, {}, 1)

    assert result is None
    db_session.commit.assert_not_called()


def test_update_contract_unauthorized_user(db_session, mock_contract, mock_user_payload):
    db_session.query().filter_by().first.side_effect = [
        mock_contract,
        Collaborator(id=1, email="user@example.com")
    ]
    mock_user_payload["role"] = "viewer"

    result = update_contract(db_session, mock_user_payload, 1, new_total_amount=1500.0)

    assert result is None
    db_session.commit.assert_not_called()


def test_update_contract_assign_new_client(db_session, mock_contract, mock_client, mock_user_payload):
    db_session.query().filter_by().first.side_effect = [
        mock_contract,
        Collaborator(id=1, email="user@example.com"),
        mock_client
    ]
    db_session.commit = MagicMock()
    db_session.refresh = MagicMock()

    updated_contract = update_contract(db_session, mock_user_payload, 1, new_client_id=2)

    assert updated_contract is not None
    assert updated_contract.client == mock_client
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(mock_contract)


def test_update_contract_invalid_new_client(db_session, mock_contract, mock_user_payload):
    db_session.query().filter_by().first.side_effect = [
        mock_contract,
        Collaborator(id=1, email="user@example.com"),
        None
    ]

    result = update_contract(db_session, mock_user_payload, 1, new_client_id=2)

    assert result is None
    db_session.commit.assert_not_called()


def test_update_contract_assign_new_commercial(db_session, mock_contract, mock_commercial, mock_user_payload):
    db_session.query().filter_by().first.side_effect = [
        mock_contract,
        Collaborator(id=1, email="user@example.com"),
        mock_commercial
    ]
    mock_user_payload["role"] = "gestion"
    db_session.commit = MagicMock()
    db_session.refresh = MagicMock()

    updated_contract = update_contract(db_session, mock_user_payload, 1, new_commercial_id=3)

    assert updated_contract is not None
    assert updated_contract.commercial == mock_commercial
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(mock_contract)


def test_update_contract_invalid_new_commercial(db_session, mock_contract, mock_user_payload):
    db_session.query().filter_by().first.side_effect = [
        mock_contract,
        Collaborator(id=1, email="user@example.com"),
        None
    ]
    mock_user_payload["role"] = "gestion"

    result = update_contract(db_session, mock_user_payload, 1, new_commercial_id=3)

    assert result is None
    db_session.commit.assert_not_called()
