from unittest.mock import MagicMock, patch

import pytest
from bl.collaborator_bl import CollaboratorBL
from dal.collaborator_dal import CollaboratorDAL
from dtos.collaborator_dto import CollaboratorDTO
from security.permissions import can_manage_collaborators
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_collaborator_dal(mock_db):
    dal = MagicMock(spec=CollaboratorDAL)
    dal.db = mock_db
    return dal


@pytest.fixture
def collaborator_bl_instance(mock_collaborator_dal):
    instance = CollaboratorBL(mock_collaborator_dal.db)
    instance.dal = mock_collaborator_dal
    return instance


@pytest.fixture
def collaborator_dto_instance():
    return CollaboratorDTO(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        role_name="Admin"
    )


@pytest.fixture
def mock_current_user():
    return {"role": "Admin", "id": 1, "email": "admin@example.com"}


def test_update_collaborator_successful(collaborator_bl_instance, mock_collaborator_dal, mock_current_user,
                                        collaborator_dto_instance):
    updates = {"name": "Jane Doe"}
    mock_collaborator_dal.update_by_id.return_value = collaborator_dto_instance
    with patch("bl.collaborator_bl.can_manage_collaborators", return_value=True):
        result = collaborator_bl_instance.update_collaborator(
            collaborator_id=1,
            updates=updates,
            current_user=mock_current_user
        )
    assert result == collaborator_dto_instance
    mock_collaborator_dal.update_by_id.assert_called_once_with(1, updates)


def test_update_collaborator_no_permission(collaborator_bl_instance, mock_collaborator_dal, mock_current_user):
    updates = {"name": "Jane Doe"}
    with patch("bl.collaborator_bl.can_manage_collaborators", return_value=False):
        with pytest.raises(PermissionError, match="Vous n'avez pas le droit de modifier un collaborateur"):
            collaborator_bl_instance.update_collaborator(
                collaborator_id=1,
                updates=updates,
                current_user=mock_current_user
            )
    mock_collaborator_dal.update_by_id.assert_not_called()


def test_update_collaborator_not_found(collaborator_bl_instance, mock_collaborator_dal, mock_current_user):
    updates = {"name": "Jane Doe"}
    mock_collaborator_dal.update_by_id.return_value = None
    with patch("bl.collaborator_bl.can_manage_collaborators", return_value=True):
        with pytest.raises(ValueError, match="collaborateur introuvable"):
            collaborator_bl_instance.update_collaborator(
                collaborator_id=99,
                updates=updates,
                current_user=mock_current_user
            )
    mock_collaborator_dal.update_by_id.assert_called_once_with(99, updates)
