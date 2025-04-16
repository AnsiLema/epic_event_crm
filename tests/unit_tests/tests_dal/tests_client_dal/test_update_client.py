from unittest.mock import MagicMock

import pytest
from dal.client_dal import ClientDAL
from dtos.client_dto import ClientDTO
from models.client import Client
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def client_dal(mock_session):
    return ClientDAL(db=mock_session)


@pytest.fixture
def client_instance():
    return Client(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        phone="1234567890",
        company="Example Inc.",
        creation_date="2023-01-01",
        last_contact_date="2023-02-01",
        commercial_id=2,
    )


def test_update_successful(client_dal, client_instance, mock_session):
    """Test the `update` method successfully updates a client and returns a DTO."""
    updates = {"name": "Jane Doe", "email": "jane.doe@example.com"}
    mock_session.refresh = MagicMock()

    result = client_dal.update(client_instance, updates)

    assert isinstance(result, ClientDTO)
    assert result.name == updates["name"]
    assert result.email == updates["email"]
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(client_instance)


def test_update_partial_fields(client_dal, client_instance, mock_session):
    """Test the `update` method with partial fields."""
    updates = {"phone": "0987654321"}
    mock_session.refresh = MagicMock()

    result = client_dal.update(client_instance, updates)

    assert isinstance(result, ClientDTO)
    assert result.phone == updates["phone"]
    assert result.name == client_instance.name
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(client_instance)


def test_update_no_fields(client_dal, client_instance, mock_session):
    """Test the `update` method when called with no fields to update."""
    updates = {}
    mock_session.refresh = MagicMock()

    result = client_dal.update(client_instance, updates)

    assert isinstance(result, ClientDTO)
    assert result.name == client_instance.name
    assert result.email == client_instance.email
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(client_instance)
