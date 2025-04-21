from unittest.mock import MagicMock, patch, ANY
import pytest
from bl.collaborator_bl import CollaboratorBL
from dtos.collaborator_dto import CollaboratorDTO
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def mock_collab_dal():
    return MagicMock()


@pytest.fixture
def mock_role_dal():
    return MagicMock()


@pytest.fixture
def collaborator_bl_instance(mock_db_session, mock_collab_dal, mock_role_dal):
    instance = CollaboratorBL(mock_db_session)
    instance.dal = mock_collab_dal
    instance.role_dal = mock_role_dal
    return instance


@pytest.fixture
def mock_current_user():
    return {"role": "admin", "permissions": ["gestion"]}


@pytest.fixture
def valid_collaborator_data():
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "password123",
        "role_name": "Manager"
    }


def test_create_collaborator_from_input_successful(mock_collab_dal, mock_role_dal):
    # Arrange
    db = MagicMock()
    collaborator_bl = CollaboratorBL(db)
    collaborator_bl.dal = mock_collab_dal
    collaborator_bl.role_dal = mock_role_dal

    mock_current_user = {
        "role": "gestion",
        "email": "admin@example.com"
    }

    valid_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "password123",
        "role_name": "gestion"
    }

    # Simuler qu'il n'existe pas déjà
    mock_collab_dal.get_by_email_raw.return_value = None
    # Simuler que le rôle existe
    mock_role_dal.get_raw_by_name.return_value = MagicMock(id=1)

    # Simuler la réponse du DAL.create
    expected_result = CollaboratorDTO(
        id=1,
        name=valid_data["name"],
        email=valid_data["email"],
        role_name="gestion"
    )
    mock_collab_dal.create.return_value = expected_result

    # Act
    result = collaborator_bl.create_collaborator_from_input(
        name=valid_data["name"],
        email=valid_data["email"],
        password=valid_data["password"],
        role_name=valid_data["role_name"],
        current_user=mock_current_user
    )

    # Assert
    mock_collab_dal.create.assert_called_once_with({
        "name": valid_data["name"],
        "email": valid_data["email"],
        "password": ANY,  # Le hash exact est imprévisible
        "role_id": 1
    })
    assert result == expected_result


def test_create_collaborator_from_input_permission_error(collaborator_bl_instance, mock_current_user,
                                                         valid_collaborator_data):
    with patch("bl.collaborator_bl.can_manage_collaborators", return_value=False):
        with pytest.raises(PermissionError, match="Vous n'avez pas le droit de créer un collaborateur"):
            collaborator_bl_instance.create_collaborator_from_input(
                name=valid_collaborator_data["name"],
                email=valid_collaborator_data["email"],
                password=valid_collaborator_data["password"],
                role_name=valid_collaborator_data["role_name"],
                current_user=mock_current_user
            )


def test_create_collaborator_from_input_missing_field(collaborator_bl_instance, mock_current_user):
    with patch("bl.collaborator_bl.can_manage_collaborators", return_value=True):
        with pytest.raises(ValueError, match="Tous les champs sont requis"):
            collaborator_bl_instance.create_collaborator_from_input(
                name=None,
                email="john.doe@example.com",
                password="password123",
                role_name="Manager",
                current_user=mock_current_user
            )


def test_create_collaborator_from_input_short_password(collaborator_bl_instance, mock_current_user,
                                                       valid_collaborator_data):
    with patch("bl.collaborator_bl.can_manage_collaborators", return_value=True):
        with pytest.raises(ValueError, match="Le mot de passe doit contenir au moins 8 caractères"):
            collaborator_bl_instance.create_collaborator_from_input(
                name=valid_collaborator_data["name"],
                email=valid_collaborator_data["email"],
                password="short",
                role_name=valid_collaborator_data["role_name"],
                current_user=mock_current_user
            )


def test_create_collaborator_from_input_duplicate_email(collaborator_bl_instance, mock_collab_dal, mock_current_user,
                                                        valid_collaborator_data):
    mock_collab_dal.get_by_email_raw.return_value = MagicMock()
    with patch("bl.collaborator_bl.can_manage_collaborators", return_value=True):
        with pytest.raises(ValueError, match="Un collaborateur avec cet email existe déjà."):
            collaborator_bl_instance.create_collaborator_from_input(
                name=valid_collaborator_data["name"],
                email=valid_collaborator_data["email"],
                password=valid_collaborator_data["password"],
                role_name=valid_collaborator_data["role_name"],
                current_user=mock_current_user
            )
    mock_collab_dal.get_by_email_raw.assert_called_once_with(valid_collaborator_data["email"])


def test_create_collaborator_from_input_invalid_role(collaborator_bl_instance, mock_role_dal, mock_current_user,
                                                     valid_collaborator_data):
    mock_role_dal.get_raw_by_name.return_value = None
    collaborator_bl_instance.dal.get_by_email_raw.return_value = None
    with patch("bl.collaborator_bl.can_manage_collaborators", return_value=True):
        with pytest.raises(ValueError, match=f"Le role '{valid_collaborator_data['role_name']}' n'existe pas."):
            collaborator_bl_instance.create_collaborator_from_input(
                name=valid_collaborator_data["name"],
                email=valid_collaborator_data["email"],
                password=valid_collaborator_data["password"],
                role_name=valid_collaborator_data["role_name"],
                current_user=mock_current_user
            )
    mock_role_dal.get_raw_by_name.assert_called_once_with(valid_collaborator_data["role_name"])


def test_create_collaborator_from_input_integrity_error(collaborator_bl_instance, mock_collab_dal, mock_role_dal,
                                                        mock_current_user, valid_collaborator_data):
    mock_role = MagicMock(id=1, name="Manager")
    mock_role_dal.get_raw_by_name.return_value = mock_role
    mock_collab_dal.get_by_email_raw.return_value = None
    mock_collab_dal.create.side_effect = IntegrityError("INSERT INTO...", {},
                                                        Exception("duplicate key"))
    with patch("bl.collaborator_bl.can_manage_collaborators", return_value=True):
        with pytest.raises(ValueError, match="Erreur: Cet email est déjà utilisé."):
            collaborator_bl_instance.create_collaborator_from_input(
                name=valid_collaborator_data["name"],
                email=valid_collaborator_data["email"],
                password=valid_collaborator_data["password"],
                role_name=valid_collaborator_data["role_name"],
                current_user=mock_current_user
            )
    mock_collab_dal.get_by_email_raw.assert_called_once_with(valid_collaborator_data["email"])
    mock_collab_dal.create.assert_called_once()


def test_create_collaborator_from_input_unexpected_exception(collaborator_bl_instance, mock_collab_dal, mock_role_dal,
                                                             mock_current_user, valid_collaborator_data):
    mock_role = MagicMock(id=1, name="Manager")
    mock_role_dal.get_raw_by_name.return_value = mock_role
    mock_collab_dal.get_by_email_raw.return_value = None
    mock_collab_dal.create.side_effect = Exception("Unexpected error")
    with patch("bl.collaborator_bl.can_manage_collaborators", return_value=True):
        with pytest.raises(ValueError, match="Une erreur inattendue est survenue : Unexpected error"):
            collaborator_bl_instance.create_collaborator_from_input(
                name=valid_collaborator_data["name"],
                email=valid_collaborator_data["email"],
                password=valid_collaborator_data["password"],
                role_name=valid_collaborator_data["role_name"],
                current_user=mock_current_user
            )
    mock_collab_dal.get_by_email_raw.assert_called_once_with(valid_collaborator_data["email"])
    mock_collab_dal.create.assert_called_once()
