from unittest.mock import MagicMock
from datetime import date
import pytest
from dal.client_dal import ClientDAL
from dtos.client_dto import ClientDTO
from models.client import Client
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    """Fixture to provide a mocked SQLAlchemy session."""
    return MagicMock(spec=Session)


@pytest.fixture
def client_dal(mock_session):
    """Fixture to create a ClientDAL instance with a mocked session."""
    return ClientDAL(mock_session)


@pytest.fixture
def client_instance():
    """Fixture to provide a sample client instance."""
    return Client(
        id=1,
        name="John Doe",
        email="johndoe@example.com",
        phone="1234567890",
        company="Doe Inc.",
        creation_date=date(2023, 1, 1),
        last_contact_date=date(2023, 6, 1),
        commercial_id=100,
    )


def test_get_existing_client(mock_session, client_dal, client_instance):
    """Test the `get` method retrieves an existing client and returns a ClientDTO."""
    mock_session.query.return_value.filter_by.return_value.first.return_value = client_instance

    result = client_dal.get(client_id=1)

    assert isinstance(result, ClientDTO)
    assert result.id == client_instance.id
    assert result.name == client_instance.name
    assert result.email == client_instance.email
    assert result.phone == client_instance.phone
    assert result.company == client_instance.company
    assert result.creation_date == client_instance.creation_date
    assert result.last_contact_date == client_instance.last_contact_date
    assert result.commercial_id == client_instance.commercial_id


def test_get_nonexistent_client(mock_session, client_dal):
    """Test the `get` method returns None when no matching client is found."""
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    result = client_dal.get(client_id=999)

    assert result is None
