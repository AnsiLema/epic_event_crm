import pytest
from unittest.mock import MagicMock, patch
from bl.collaborator_bl import CollaboratorBL
from dtos.collaborator_dto import CollaboratorDTO


@pytest.fixture
def collaborator_bl():
    fake_db = MagicMock()
    bl = CollaboratorBL(fake_db)
    bl.dal = MagicMock()
    bl.role_dal = MagicMock()
    return bl


@patch("bl.collaborator_bl.can_manage_collaborators", return_value=True)
def test_create_collaborator_success(mock_permission, collaborator_bl):
    # Arrange
    fake_user = {"sub": "admin@example.com", "role": "gestionnaire"}
    fake_data = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "securepass123",
        "role_id": 2
    }

    expected_result = CollaboratorDTO(
        id=1,
        name="Alice",
        email="alice@example.com",
        role_name="commercial"
    )

    collaborator_bl.dal.create.return_value = expected_result

    # Act
    result = collaborator_bl.create_collaborator(fake_data, fake_user)

    # Assert
    assert isinstance(result, CollaboratorDTO)
    assert result.name == "Alice"
    assert result.email == "alice@example.com"
    assert result.role_name == "commercial"


@patch("bl.collaborator_bl.can_manage_collaborators", return_value=False)
def test_create_collaborator_permission_denied(mock_permission, collaborator_bl):
    # Arrange
    fake_user = {"sub": "commercial@example.com", "role": "commercial"}
    fake_data = {
        "name": "Bob",
        "email": "bob@example.com",
        "password": "password123",
        "role_id": 3
    }

    # Act + Assert
    with pytest.raises(PermissionError, match="Vous n'avez pas le droit de créer un collaborateur"):
        collaborator_bl.create_collaborator(fake_data, fake_user)
