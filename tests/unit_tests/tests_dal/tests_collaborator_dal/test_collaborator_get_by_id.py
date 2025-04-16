from unittest.mock import Mock

import pytest
from dal.collaborator_dal import CollaboratorDAL
from models.role import Role
from models.collaborator import Collaborator
from sqlalchemy.orm import Session
from dtos.collaborator_dto import CollaboratorDTO


@pytest.fixture
def mock_session():
    return Mock(spec=Session)


@pytest.fixture
def collaborator_dal(mock_session):
    return CollaboratorDAL(db=mock_session)


def test_get_by_id_found(collaborator_dal, mock_session):
    role = Role(id=2, name="Support")
    collaborator = Collaborator(id=1, name="John Doe", email="john@example.com", role_id=2)
    collaborator.role = role

    mock_session.query.return_value.filter_by.return_value.first.return_value = collaborator

    result = collaborator_dal.get_by_id(1)

    assert isinstance(result, CollaboratorDTO)
    assert result.name == "John Doe"
    assert result.role_name == "Support"


def test_get_by_id_not_found(collaborator_dal, mock_session):
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    result = collaborator_dal.get_by_id(collaborator_id=1)

    assert result is None
