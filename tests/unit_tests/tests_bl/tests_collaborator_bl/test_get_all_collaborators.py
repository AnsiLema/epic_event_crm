from unittest.mock import MagicMock, patch

import pytest
from bl.collaborator_bl import CollaboratorBL
from dal.collaborator_dal import CollaboratorDAL
from dtos.collaborator_dto import CollaboratorDTO
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_collaborator_dal(mock_db_session):
    return MagicMock(spec=CollaboratorDAL, db=mock_db_session)


@pytest.fixture
def collaborator_bl_instance(mock_collaborator_dal):
    collaborator_bl = CollaboratorBL(db=mock_collaborator_dal.db)
    collaborator_bl.dal = mock_collaborator_dal
    return collaborator_bl


def test_get_all_collaborators_success(collaborator_bl_instance, mock_collaborator_dal):
    mock_collaborators = [
        CollaboratorDTO(id=1, name="John Doe", email="john.doe@example.com", role_name="Manager"),
        CollaboratorDTO(id=2, name="Jane Smith", email="jane.smith@example.com", role_name="Employee"),
    ]
    mock_collaborator_dal.get_all.return_value = mock_collaborators

    result = collaborator_bl_instance.get_all_collaborators()

    assert result == mock_collaborators
    mock_collaborator_dal.get_all.assert_called_once()


def test_get_all_collaborators_empty_list(collaborator_bl_instance, mock_collaborator_dal):
    mock_collaborator_dal.get_all.return_value = []

    result = collaborator_bl_instance.get_all_collaborators()

    assert result == []
    mock_collaborator_dal.get_all.assert_called_once()
