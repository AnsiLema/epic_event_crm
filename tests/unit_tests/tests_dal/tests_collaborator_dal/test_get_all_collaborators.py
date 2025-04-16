from unittest.mock import MagicMock, create_autospec

import pytest
from dal.collaborator_dal import CollaboratorDAL
from dtos.collaborator_dto import CollaboratorDTO
from models.collaborator import Collaborator
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db_session():
    return create_autospec(Session)


@pytest.fixture
def collaborator_dal(mock_db_session):
    return CollaboratorDAL(mock_db_session)


def test_get_all_with_no_collaborators(collaborator_dal, mock_db_session):
    mock_db_session.query.return_value.all.return_value = []

    result = collaborator_dal.get_all()

    assert result == []
    mock_db_session.query.assert_called_once_with(Collaborator)
    mock_db_session.query.return_value.all.assert_called_once()


def test_get_all_with_multiple_collaborators(collaborator_dal, mock_db_session):
    mock_collaborators = [
        Collaborator(id=1, name="John Doe", email="john@example.com", role_id=1),
        Collaborator(id=2, name="Jane Smith", email="jane@example.com", role_id=2),
    ]
    mock_db_session.query.return_value.all.return_value = mock_collaborators

    collaborator_dal._to_dto = MagicMock(side_effect=lambda c: CollaboratorDTO(
        id=c.id,
        name=c.name,
        email=c.email,
        role_name=f"Role {c.role_id}"
    ))

    result = collaborator_dal.get_all()

    assert len(result) == 2
    assert result[0] == CollaboratorDTO(id=1, name="John Doe", email="john@example.com", role_name="Role 1")
    assert result[1] == CollaboratorDTO(id=2, name="Jane Smith", email="jane@example.com", role_name="Role 2")
    mock_db_session.query.assert_called_once_with(Collaborator)
    mock_db_session.query.return_value.all.assert_called_once()
    collaborator_dal._to_dto.assert_any_call(mock_collaborators[0])
    collaborator_dal._to_dto.assert_any_call(mock_collaborators[1])
