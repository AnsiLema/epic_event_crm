from unittest.mock import MagicMock, patch

import pytest
from bl.client_bl import ClientBLL
from dal.client_dal import ClientDAL
from dal.collaborator_dal import CollaboratorDAL
from dtos.client_dto import ClientDTO
from security.permissions import is_commercial
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_client_dal(mock_session):
    return MagicMock(spec=ClientDAL, db=mock_session)


@pytest.fixture
def mock_collaborator_dal(mock_session):
    return MagicMock(spec=CollaboratorDAL, db=mock_session)


@pytest.fixture
def client_bl_instance(mock_client_dal, mock_collaborator_dal):
    bl_instance = ClientBLL(mock_client_dal.db)
    bl_instance.dal = mock_client_dal
    bl_instance.collaborator_dal = mock_collaborator_dal
    return bl_instance


@pytest.fixture
def mock_current_user():
    return {"sub": "user@example.com", "role": "commercial"}


@pytest.fixture
def client_dto_instance():
    return ClientDTO(
        id=1,
        name="Client Name",
        email="client@example.com",
        phone="123456789",
        company="Client Company",
        creation_date=None,
        last_contact_date=None,
        commercial_id=42,
    )


def test_update_client_successful(client_bl_instance, mock_client_dal, mock_collaborator_dal, mock_current_user,
                                  client_dto_instance):
    mock_collaborator = MagicMock(id=42, email=mock_current_user["sub"])
    mock_collaborator_dal.get_by_email_raw.return_value = mock_collaborator
    mock_client_dal.get.return_value = client_dto_instance
    mock_client_dal.update_by_id.return_value = client_dto_instance
    updates = {"name": "Updated Client Name"}

    with patch("security.permissions.is_commercial", return_value=True):
        result = client_bl_instance.update_client(client_id=1, updates=updates, current_user=mock_current_user)

    assert result == client_dto_instance
    mock_collaborator_dal.get_by_email_raw.assert_called_once_with(mock_current_user["sub"])
    mock_client_dal.get.assert_called_once_with(1)
    mock_client_dal.update_by_id.assert_called_once_with(1, updates)


def test_update_client_permission_denied(client_bl_instance, mock_current_user):
    non_commercial_user = {"sub": "noncommercial@example.com", "role": "user"}
    updates = {"name": "Updated Client Name"}

    with patch("security.permissions.is_commercial", return_value=False), pytest.raises(PermissionError):
        client_bl_instance.update_client(client_id=1, updates=updates, current_user=non_commercial_user)


def test_update_client_collaborator_not_found(client_bl_instance, mock_collaborator_dal, mock_current_user):
    mock_collaborator_dal.get_by_email_raw.return_value = None
    updates = {"name": "Updated Client Name"}

    with patch("security.permissions.is_commercial", return_value=True), pytest.raises(ValueError,
                                                                                       match="collaborateur introuvable"):
        client_bl_instance.update_client(client_id=1, updates=updates, current_user=mock_current_user)

    mock_collaborator_dal.get_by_email_raw.assert_called_once_with(mock_current_user["sub"])


def test_update_client_not_found(client_bl_instance, mock_collaborator_dal, mock_client_dal, mock_current_user):
    mock_collaborator = MagicMock(id=42, email=mock_current_user["sub"])
    mock_collaborator_dal.get_by_email_raw.return_value = mock_collaborator
    mock_client_dal.get.return_value = None
    updates = {"name": "Updated Client Name"}

    with patch("security.permissions.is_commercial", return_value=True), pytest.raises(ValueError,
                                                                                       match="client introuvable"):
        client_bl_instance.update_client(client_id=1, updates=updates, current_user=mock_current_user)

    mock_collaborator_dal.get_by_email_raw.assert_called_once_with(mock_current_user["sub"])
    mock_client_dal.get.assert_called_once_with(1)


def test_update_client_wrong_commercial(client_bl_instance, mock_collaborator_dal, mock_client_dal, mock_current_user,
                                        client_dto_instance):
    mock_collaborator = MagicMock(id=99, email=mock_current_user["sub"])
    mock_collaborator_dal.get_by_email_raw.return_value = mock_collaborator
    mock_client_dal.get.return_value = client_dto_instance
    updates = {"name": "Updated Client Name"}

    with patch("security.permissions.is_commercial", return_value=True), pytest.raises(PermissionError,
                                                                                       match="Vous ne pouvez modifier que vos propres clients."):
        client_bl_instance.update_client(client_id=1, updates=updates, current_user=mock_current_user)

    mock_collaborator_dal.get_by_email_raw.assert_called_once_with(mock_current_user["sub"])
    mock_client_dal.get.assert_called_once_with(1)
