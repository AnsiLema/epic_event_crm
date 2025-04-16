import pytest
from dal.collaborator_dal import CollaboratorDAL
from models.collaborator import Collaborator
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db_session():
    """Fixture for providing a mock SQLAlchemy session."""
    from unittest.mock import MagicMock
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def collaborator_dal(mock_db_session):
    """Fixture for initializing the CollaboratorDAL with a mock session."""
    return CollaboratorDAL(db=mock_db_session)


def test_get_by_email_raw_with_existing_email(collaborator_dal, mock_db_session):
    """Test that get_by_email_raw successfully returns a collaborator when the email exists."""
    mock_collaborator = Collaborator(id=1, name="John Doe", email="john.doe@example.com", password="hashed_password",
                                     role_id=2)
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_collaborator

    result = collaborator_dal.get_by_email_raw("john.doe@example.com")

    assert result == mock_collaborator
    mock_db_session.query.assert_called_once()
    mock_db_session.query.return_value.filter_by.assert_called_once_with(email="john.doe@example.com")


def test_get_by_email_raw_with_non_existing_email(collaborator_dal, mock_db_session):
    """Test that get_by_email_raw returns None when the email does not exist."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

    result = collaborator_dal.get_by_email_raw("non.existing@example.com")

    assert result is None
    mock_db_session.query.assert_called_once()
    mock_db_session.query.return_value.filter_by.assert_called_once_with(email="non.existing@example.com")
