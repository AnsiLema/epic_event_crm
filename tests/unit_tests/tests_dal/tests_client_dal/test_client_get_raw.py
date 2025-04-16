from unittest.mock import MagicMock

import pytest
from dal.client_dal import ClientDAL
from models.client import Client


@pytest.fixture
def mock_session():
    """Fixture for mocking the SQLAlchemy session."""
    return MagicMock()


@pytest.fixture
def client_dal(mock_session):
    """Fixture for creating a ClientDAL instance."""
    return ClientDAL(db=mock_session)


def test_get_raw_existing_client(client_dal, mock_session):
    """Test the `get_raw` method when the client exists."""
    mock_client = Client(id=1, name="John Doe", email="john.doe@example.com")
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_client

    result = client_dal.get_raw(client_id=1)

    assert result == mock_client
    mock_session.query.assert_called_once_with(Client)
    mock_session.query.return_value.filter_by.assert_called_once_with(id=1)


def test_get_raw_nonexistent_client(client_dal, mock_session):
    """Test the `get_raw` method when the client does not exist."""
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    result = client_dal.get_raw(client_id=999)

    assert result is None
    mock_session.query.assert_called_once_with(Client)
    mock_session.query.return_value.filter_by.assert_called_once_with(id=999)
