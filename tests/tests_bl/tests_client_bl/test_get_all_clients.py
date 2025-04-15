from unittest.mock import MagicMock, patch

import pytest
from bl.client_bl import ClientBLL
from dal.client_dal import ClientDAL
from dtos.client_dto import ClientDTO
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_client_dal(mock_session):
    return MagicMock(spec=ClientDAL, db=mock_session)


@pytest.fixture
def client_bl_instance(mock_client_dal):
    client_bl = ClientBLL(db=mock_client_dal.db)
    client_bl.dal = mock_client_dal
    return client_bl


def test_get_all_clients_successfully(client_bl_instance, mock_client_dal):
    # Arrange
    mock_clients = [
        ClientDTO(id=1, name="Client 1", email="client1@example.com", phone="1234567890",
                  company="Company A", creation_date="2023-01-01", last_contact_date=None, commercial_id=101),
        ClientDTO(id=2, name="Client 2", email="client2@example.com", phone=None,
                  company="Company B", creation_date="2023-02-01", last_contact_date="2023-02-15", commercial_id=102)
    ]
    mock_client_dal.get_all.return_value = mock_clients

    # Act
    result = client_bl_instance.get_all_clients()

    # Assert
    assert result == mock_clients
    mock_client_dal.get_all.assert_called_once()


def test_get_all_clients_empty(client_bl_instance, mock_client_dal):
    # Arrange
    mock_client_dal.get_all.return_value = []

    # Act
    result = client_bl_instance.get_all_clients()

    # Assert
    assert result == []
    mock_client_dal.get_all.assert_called_once()
