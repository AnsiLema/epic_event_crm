from unittest.mock import MagicMock

import pytest
from dal.collaborator_dal import CollaboratorDAL
from dtos.collaborator_dto import CollaboratorDTO
from models.collaborator import Collaborator
from sqlalchemy.orm import Session


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def collaborator_dal(db_session):
    return CollaboratorDAL(db_session)


def test_update_by_id_success(collaborator_dal, db_session):
    mock_collaborator = MagicMock(spec=Collaborator, id=1, name="Old Name", email="old_email@example.com")
    db_session.query.return_value.filter_by.return_value.first.return_value = mock_collaborator
    updated_data = {"name": "New Name", "email": "new_email@example.com"}

    result = collaborator_dal.update_by_id(1, updated_data)

    assert result is not None
    assert isinstance(result, CollaboratorDTO)
    assert result.name == "New Name"
    assert result.email == "new_email@example.com"


def test_update_by_id_no_collaborator_found(collaborator_dal, db_session):
    db_session.query.return_value.filter_by.return_value.first.return_value = None
    updates = {"name": "New Name"}

    result = collaborator_dal.update_by_id(999, updates)

    assert result is None


def test_update_by_id_partial_update(collaborator_dal, db_session):
    mock_collaborator = MagicMock(spec=Collaborator, id=1, name="Old Name", email="old_email@example.com")
    db_session.query.return_value.filter_by.return_value.first.return_value = mock_collaborator
    updates = {"email": "updated_email@example.com"}

    result = collaborator_dal.update_by_id(1, updates)

    assert result is not None
    assert isinstance(result, CollaboratorDTO)
    assert result.name == mock_collaborator.name  # Name should remain unchanged
    assert result.email == "updated_email@example.com"
