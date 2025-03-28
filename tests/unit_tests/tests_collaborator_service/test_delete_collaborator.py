from unittest.mock import MagicMock, patch
import pytest
from models.collaborator import Collaborator
from services.collaborator_service import delete_collaborator


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def collaborator_data():
    return {"id": 1, "name": "John Doe", "email": "johndoe@example.com", "role_id": 1}


@pytest.fixture
def valid_payload():
    return {"role": "admin", "permissions": ["gestion"]}


@pytest.fixture
def invalid_payload():
    return {"role": "user", "permissions": []}


def test_delete_collaborator_success(mock_db_session, valid_payload, collaborator_data):
    collaborator = MagicMock(spec=Collaborator, **collaborator_data)
    mock_db_session.query().filter_by().first.return_value = collaborator

    with patch("services.collaborator_service.can_manage_collaborators", return_value=True):
        result = delete_collaborator(mock_db_session, valid_payload, collaborator_data["id"])

    assert result is True
    mock_db_session.delete.assert_called_once_with(collaborator)
    mock_db_session.commit.assert_called_once()


def test_delete_collaborator_permission_denied(mock_db_session, invalid_payload, collaborator_data):
    with patch("services.collaborator_service.can_manage_collaborators", return_value=False):
        result = delete_collaborator(mock_db_session, invalid_payload, collaborator_data["id"])

    assert result is False
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_delete_collaborator_not_found(mock_db_session, valid_payload):
    mock_db_session.query().filter_by().first.return_value = None

    with patch("services.collaborator_service.can_manage_collaborators", return_value=True):
        result = delete_collaborator(mock_db_session, valid_payload, 999)

    assert result is False
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_delete_collaborator_invalid_payload_type(mock_db_session):
    with pytest.raises(TypeError):
        delete_collaborator(mock_db_session, "invalid_payload", 1)
