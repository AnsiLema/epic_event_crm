from unittest.mock import MagicMock

import pytest
from models.client import Client
from models.collaborator import Collaborator
from services.reader_service import get_clients_by_commercial


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def sample_clients():
    return [
        Client(id=1, name="Client One", email="client1@example.com"),
        Client(id=2, name="Client Two", email="client2@example.com"),
    ]


def test_get_clients_by_commercial_returns_clients(mock_session, sample_clients):
    mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = sample_clients

    commercial_email = "commercial@example.com"
    result = get_clients_by_commercial(mock_session, commercial_email)

    assert result == sample_clients
    mock_session.query.assert_called_once_with(Client)
    mock_session.query.return_value.join.assert_called_once_with(Collaborator)
    mock_session.query.return_value.join.return_value.filter.assert_called_once()


def test_get_clients_by_commercial_no_clients_found(mock_session):
    mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = []

    commercial_email = "nonexistent@example.com"
    result = get_clients_by_commercial(mock_session, commercial_email)

    assert result == []
    mock_session.query.assert_called_once_with(Client)
    mock_session.query.return_value.join.assert_called_once_with(Collaborator)
    mock_session.query.return_value.join.return_value.filter.assert_called_once()
