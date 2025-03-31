# tests/test_contract_service.py

from unittest.mock import MagicMock

import pytest
from models.client import Client
from models.collaborator import Collaborator
from models.contract import Contract
from services.contract_service import create_contract


@pytest.fixture
def db_session():
    return MagicMock()


@pytest.fixture
def payload():
    return {"role": "gestion"}


def test_create_contract_success(db_session, payload):
    # Arrange
    mock_client = MagicMock(spec=Client, id=1)
    mock_commercial = MagicMock(spec=Collaborator, id=2)

    mock_role = MagicMock()
    mock_role.name = "commercial"
    mock_commercial.role = mock_role

    db_session.query.return_value.filter_by.side_effect = [
        MagicMock(first=lambda: mock_client),  # Mock client query
        MagicMock(first=lambda: mock_commercial),  # Mock commercial query
    ]

    # Act
    result = create_contract(
        db=db_session,
        payload=payload,
        client_id=1,
        commercial_id=2,
        total_amount=1500.0,
        amount_left=500.0,
        is_signed=True
    )

    # Assert
    assert result is not None
    assert isinstance(result, Contract)
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(result)


def test_create_contract_invalid_role(db_session, payload):
    # Arrange
    payload["role"] = "user"

    # Act
    result = create_contract(
        db=db_session,
        payload=payload,
        client_id=1,
        commercial_id=2,
        total_amount=1500.0,
        amount_left=500.0,
        is_signed=True
    )

    # Assert
    assert result is None
    db_session.add.assert_not_called()
    db_session.commit.assert_not_called()


def test_create_contract_client_not_found(db_session, payload):
    # Arrange
    db_session.query.return_value.filter_by.return_value.first.return_value = None

    # Act
    result = create_contract(
        db=db_session,
        payload=payload,
        client_id=1,
        commercial_id=2,
        total_amount=1500.0,
        amount_left=500.0,
        is_signed=True
    )

    # Assert
    assert result is None
    db_session.add.assert_not_called()
    db_session.commit.assert_not_called()


def test_create_contract_commercial_not_found(db_session, payload):
    # Arrange
    mock_client = MagicMock(spec=Client, id=1)
    db_session.query.return_value.filter_by.side_effect = [
        MagicMock(first=lambda: mock_client),  # Mock client query
        MagicMock(first=lambda: None),  # Mock commercial not found
    ]

    # Act
    result = create_contract(
        db=db_session,
        payload=payload,
        client_id=1,
        commercial_id=2,
        total_amount=1500.0,
        amount_left=500.0,
        is_signed=True
    )

    # Assert
    assert result is None
    db_session.add.assert_not_called()
    db_session.commit.assert_not_called()


def test_create_contract_commercial_invalid_role(db_session, payload):
    # Arrange
    mock_client = MagicMock(spec=Client, id=1)
    mock_commercial = MagicMock(spec=Collaborator, id=2)
    mock_commercial.role = MagicMock(name="support")  # Invalid role
    db_session.query.return_value.filter_by.side_effect = [
        MagicMock(first=lambda: mock_client),  # Mock client query
        MagicMock(first=lambda: mock_commercial),  # Mock invalid commercial role
    ]

    # Act
    result = create_contract(
        db=db_session,
        payload=payload,
        client_id=1,
        commercial_id=2,
        total_amount=1500.0,
        amount_left=500.0,
        is_signed=True
    )

    # Assert
    assert result is None
    db_session.add.assert_not_called()
    db_session.commit.assert_not_called()
