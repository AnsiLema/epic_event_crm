from unittest.mock import MagicMock, patch

import pytest
from models.collaborator import Collaborator
from security.auth_service import authenticate_collaborator
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_collaborator():
    collaborator = Collaborator(
        id=1,
        name="Test User",
        email="test@example.com",
        password="hashed_password",
        role_id=1
    )
    return collaborator


def test_authenticate_collaborator_success(mock_db_session, mock_collaborator):
    mock_db_session.query().filter_by().first.return_value = mock_collaborator

    with patch("services.auth_service.verify_password", return_value=True):
        result = authenticate_collaborator(
            db=mock_db_session,
            email="test@example.com",
            password="correct_password"
        )
        assert result == mock_collaborator


def test_authenticate_collaborator_user_not_found(mock_db_session):
    mock_db_session.query().filter_by().first.return_value = None

    result = authenticate_collaborator(
        db=mock_db_session,
        email="nonexistent@example.com",
        password="any_password"
    )
    assert result is None


def test_authenticate_collaborator_incorrect_password(mock_db_session, mock_collaborator):
    mock_db_session.query().filter_by().first.return_value = mock_collaborator

    with patch("services.auth_service.verify_password", return_value=False):
        result = authenticate_collaborator(
            db=mock_db_session,
            email="test@example.com",
            password="wrong_password"
        )
        assert result is None


def test_authenticate_collaborator_no_password_verification_call(mock_db_session):
    mock_db_session.query().filter_by().first.return_value = None

    with patch("security.password.verify_password") as mock_verify_password:
        result = authenticate_collaborator(
            db=mock_db_session,
            email="test@example.com",
            password="any_password"
        )
        mock_verify_password.assert_not_called()
        assert result is None
