from unittest.mock import Mock

import pytest
from dal.collaborator_dal import CollaboratorDAL
from dtos.collaborator_dto import CollaboratorDTO
from models.collaborator import Collaborator


@pytest.fixture
def mock_db_session():
    return Mock()


@pytest.fixture
def collaborator_dal(mock_db_session):
    return CollaboratorDAL(db=mock_db_session)


@pytest.fixture
def sample_collaborator():
    collaborator = Collaborator(
        id=1,
        name="John Doe",
        email="johndoe@example.com",
        password="securepassword123",
        role_id=1
    )
    return collaborator


def test_get_by_email_existing(collaborator_dal, mock_db_session, sample_collaborator):
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_collaborator
    collaborator_dal._to_dto = Mock(return_value=CollaboratorDTO(
        id=sample_collaborator.id,
        name=sample_collaborator.name,
        email=sample_collaborator.email,
        role_name="Admin"
    ))

    result = collaborator_dal.get_by_email(email="johndoe@example.com")

    assert result is not None
    assert result.id == sample_collaborator.id
    assert result.name == sample_collaborator.name
    assert result.email == sample_collaborator.email
    assert result.role_name == "Admin"


def test_get_by_email_non_existing(collaborator_dal, mock_db_session):
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

    result = collaborator_dal.get_by_email(email="nonexistent@example.com")

    assert result is None
