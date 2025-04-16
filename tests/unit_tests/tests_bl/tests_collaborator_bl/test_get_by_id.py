from unittest.mock import MagicMock, patch

import pytest
from bl.collaborator_bl import CollaboratorBL
from dal.collaborator_dal import CollaboratorDAL
from dtos.collaborator_dto import CollaboratorDTO
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def collaborator_dal(mock_session):
    return MagicMock(spec=CollaboratorDAL)


@pytest.fixture
def collaborator_bl_instance(collaborator_dal):
    collaborator_bl = CollaboratorBL.__new__(CollaboratorBL)
    collaborator_bl.dal = collaborator_dal
    return collaborator_bl


def test_get_by_id_successful(collaborator_bl_instance, collaborator_dal):
    mock_collaborator_dto = CollaboratorDTO(id=1, name="John Doe", email="john.doe@example.com", role_name="Admin")
    collaborator_dal.get_by_id.return_value = mock_collaborator_dto

    result = collaborator_bl_instance.get_by_id(1)

    assert result == mock_collaborator_dto
    collaborator_dal.get_by_id.assert_called_once_with(1)


def test_get_by_id_not_found(collaborator_bl_instance, collaborator_dal):
    collaborator_dal.get_by_id.return_value = None

    with pytest.raises(ValueError, match="collaborateur introuvable"):
        collaborator_bl_instance.get_by_id(999)

    collaborator_dal.get_by_id.assert_called_once_with(999)
