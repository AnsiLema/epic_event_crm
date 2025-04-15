from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from bl.client_bl import ClientBLL
from dal.client_dal import ClientDAL
from dal.collaborator_dal import CollaboratorDAL
from dtos.client_dto import ClientDTO
from security.permissions import is_commercial
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_client_dal(mock_db_session):
    return MagicMock(spec=ClientDAL, db=mock_db_session)


@pytest.fixture
def mock_collab_dal(mock_db_session):
    return MagicMock(spec=CollaboratorDAL, db=mock_db_session)


@pytest.fixture
def client_bl_instance(mock_client_dal, mock_collab_dal):
    client_bl = ClientBLL(mock_client_dal.db)
    client_bl.dal = mock_client_dal
    client_bl.collaborator_dal = mock_collab_dal
    return client_bl


@pytest.fixture
def mock_current_user():
    return {"sub": "user@example.com", "role": "commercial"}


@pytest.fixture
def client_dto_instance():
    return ClientDTO(
        id=1,
        name="Test Client",
        email="test@example.com",
        phone="1234567890",
        company="Test Company",
        creation_date=date(2023, 1, 1),
        last_contact_date=None,
        commercial_id=42
    )


def test_update_client_from_input_successful(client_bl_instance, mock_client_dal, mock_collab_dal, mock_current_user,
                                             client_dto_instance):
    mock_collaborator = MagicMock(id=42, email=mock_current_user["sub"])
    mock_collab_dal.get_by_email_raw.return_value = mock_collaborator
    mock_client_dal.get.return_value = client_dto_instance
    mock_client_dal.update_by_id.return_value = client_dto_instance

    with patch("security.permissions.is_commercial", return_value=True):
        result = client_bl_instance.update_client_from_input(
            client_id=1,
            name="Updated Name",
            email=None,
            phone=None,
            company=None,
            current_user=mock_current_user
        )

    assert result == client_dto_instance
    mock_collab_dal.get_by_email_raw.assert_called_once_with(mock_current_user["sub"])
    mock_client_dal.get.assert_called_once_with(1)
    mock_client_dal.update_by_id.assert_called_once_with(1, {"name": "Updated Name"})


def test_update_client_from_input_no_permissions(client_bl_instance, mock_current_user):
    with patch("security.permissions.is_commercial", return_value=False):
        with pytest.raises(PermissionError, match="Vous ne pouvez modifier que vos propres clients."):
            client_bl_instance.update_client_from_input(
                client_id=1,
                name="Updated Name",
                email=None,
                phone=None,
                company=None,
                current_user=mock_current_user
            )


def test_update_client_from_input_missing_collaborator(client_bl_instance, mock_collab_dal, mock_current_user):
    mock_collab_dal.get_by_email_raw.return_value = None

    with patch("security.permissions.is_commercial", return_value=True):
        with pytest.raises(ValueError, match="collaborateur introuvable"):
            client_bl_instance.update_client_from_input(
                client_id=1,
                name="Updated Name",
                email=None,
                phone=None,
                company=None,
                current_user=mock_current_user
            )


def test_update_client_from_input_missing_client(client_bl_instance, mock_client_dal, mock_collab_dal,
                                                 mock_current_user):
    mock_collaborator = MagicMock(id=42, email=mock_current_user["sub"])
    mock_collab_dal.get_by_email_raw.return_value = mock_collaborator
    mock_client_dal.get.return_value = None

    with patch("security.permissions.is_commercial", return_value=True):
        with pytest.raises(ValueError, match="client introuvable"):
            client_bl_instance.update_client_from_input(
                client_id=1,
                name="Updated Name",
                email=None,
                phone=None,
                company=None,
                current_user=mock_current_user
            )


def test_update_client_from_input_unauthorized_client_access(client_bl_instance, mock_client_dal, mock_collab_dal,
                                                             mock_current_user, client_dto_instance):
    mock_collaborator = MagicMock(id=99, email=mock_current_user["sub"])
    mock_collab_dal.get_by_email_raw.return_value = mock_collaborator
    mock_client_dal.get.return_value = client_dto_instance

    with patch("security.permissions.is_commercial", return_value=True):
        with pytest.raises(PermissionError, match="Vous ne pouvez modifier que vos propres clients."):
            client_bl_instance.update_client_from_input(
                client_id=1,
                name="Updated Name",
                email=None,
                phone=None,
                company=None,
                current_user=mock_current_user
            )
