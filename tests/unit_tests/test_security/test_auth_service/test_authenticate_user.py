from unittest.mock import Mock, patch

import pytest
from security.auth_service import authenticate_collaborator


def test_authenticate_collaborator_success():
    mock_db = Mock()

    mock_role = Mock()
    mock_role.name = "Admin"

    mock_user = Mock(
        id=1,
        name="Jean Test",
        email="test@example.com",
        password="hashed_password",
        role=mock_role
    )

    mock_collaborator_dal = Mock()
    mock_collaborator_dal.get_by_email_raw.return_value = mock_user

    with patch("security.auth_service.CollaboratorDAL", return_value=mock_collaborator_dal), \
         patch("security.auth_service.verify_password", return_value=True):

        result = authenticate_collaborator(mock_db, "test@example.com", "plain_password")

        assert result == {
            "id": 1,
            "sub": "test@example.com",
            "email": "test@example.com",
            "role": "Admin"
        }


def test_authenticate_collaborator_invalid_password():
    mock_db = Mock()
    mock_user = Mock(password="hashed_password")
    mock_collaborator_dal = Mock()
    mock_collaborator_dal.get_by_email_raw.return_value = mock_user

    with patch("security.auth_service.CollaboratorDAL", return_value=mock_collaborator_dal), \
            patch("security.auth_service.verify_password", return_value=False):
        result = authenticate_collaborator(mock_db, "test@example.com", "wrong_password")

    assert result is None


def test_authenticate_collaborator_user_not_found():
    mock_db = Mock()
    mock_collaborator_dal = Mock()
    mock_collaborator_dal.get_by_email_raw.return_value = None

    with patch("security.auth_service.CollaboratorDAL", return_value=mock_collaborator_dal):
        result = authenticate_collaborator(mock_db, "nonexistent@example.com", "any_password")

    assert result is None


def test_authenticate_collaborator_missing_role():
    mock_db = Mock()
    mock_user = Mock(id=2, name="Jean Test", email="user@example.com", password="hashed_password", role=None)
    mock_collaborator_dal = Mock()
    mock_collaborator_dal.get_by_email_raw.return_value = mock_user

    with patch("security.auth_service.CollaboratorDAL", return_value=mock_collaborator_dal), \
         patch("security.auth_service.verify_password", return_value=True):
        with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'name'"):
            authenticate_collaborator(mock_db, "user@example.com", "correct_password")