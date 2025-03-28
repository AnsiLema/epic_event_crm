from unittest.mock import MagicMock

import pytest
from models.client import Client
from services.reader_service import get_all_clients


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def sample_clients():
    return [
        Client(id=1, name="Client A", email="clienta@example.com"),
        Client(id=2, name="Client B", email="clientb@example.com"),
    ]


def test_get_all_clients_returns_clients(mock_db_session, sample_clients):
    # Arrange
    mock_db_session.query.return_value.all.return_value = sample_clients

    # Act
    result = get_all_clients(mock_db_session)

    # Assert
    assert result == sample_clients
    mock_db_session.query.assert_called_once()
    mock_db_session.query().all.assert_called_once()


def test_get_all_clients_returns_empty_list(mock_db_session):
    # Arrange
    mock_db_session.query.return_value.all.return_value = []

    # Act
    result = get_all_clients(mock_db_session)

    # Assert
    assert result == []
    mock_db_session.query.assert_called_once()
    mock_db_session.query().all.assert_called_once()
