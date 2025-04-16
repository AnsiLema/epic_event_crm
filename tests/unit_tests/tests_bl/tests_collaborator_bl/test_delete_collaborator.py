from unittest.mock import MagicMock, patch

import pytest
from bl.collaborator_bl import CollaboratorBL
from dal.collaborator_dal import CollaboratorDAL
from security.permissions import can_manage_collaborators
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_collaborator_dal(mock_db_session):
    return MagicMock(spec=CollaboratorDAL, db=mock_db_session)


@pytest.fixture
def collaborator_bl_instance(mock_collaborator_dal):
    collaborator_bl = CollaboratorBL(MagicMock(spec=Session))
    collaborator_bl.dal = mock_collaborator_dal
    return collaborator_bl


@pytest.fixture
def mock_current_user():
    return {"id": 1, "email": "user@example.com", "role": "admin"}


def test_delete_collaborator_successful(collaborator_bl_instance, mock_collaborator_dal, mock_current_user):
    mock_collaborator_dal.delete_by_id.return_value = True
    with patch("bl.collaborator_bl.can_manage_collaborators", return_value=True):
        result = collaborator_bl_instance.delete_collaborator(1, mock_current_user)
    assert result is None
    mock_collaborator_dal.delete_by_id.assert_called_once_with(1)


def test_delete_collaborator_permission_error(collaborator_bl_instance, mock_current_user):
    with patch("bl.collaborator_bl.can_manage_collaborators", return_value=False):
        with pytest.raises(PermissionError, match="Vous n'avez pas le droit de supprimer un collaborateur"):
            collaborator_bl_instance.delete_collaborator(1, mock_current_user)


def test_delete_collaborator_not_found(collaborator_bl_instance, mock_collaborator_dal, mock_current_user):
    mock_collaborator_dal.delete_by_id.return_value = False
    with patch("bl.collaborator_bl.can_manage_collaborators", return_value=True):
        with pytest.raises(ValueError, match="collaborateur introuvable"):
            collaborator_bl_instance.delete_collaborator(1, mock_current_user)
    mock_collaborator_dal.delete_by_id.assert_called_once_with(1)
