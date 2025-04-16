from datetime import date
from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy.exc import IntegrityError

from bl.client_bl import ClientBLL
from dal.client_dal import ClientDAL
from dal.collaborator_dal import CollaboratorDAL
from dtos.client_dto import ClientDTO
from security.permissions import is_commercial


@pytest.fixture
def db_session():
    return MagicMock()


@pytest.fixture
def client_dal(db_session):
    return MagicMock(ClientDAL(db_session))


@pytest.fixture
def collaborator_dal(db_session):
    return MagicMock(CollaboratorDAL(db_session))


@pytest.fixture
def client_bl_instance(client_dal, collaborator_dal):
    instance = ClientBLL(db=MagicMock())
    instance.dal = client_dal
    instance.collaborator_dal = collaborator_dal
    return instance


@pytest.fixture
def mock_current_user():
    return {"sub": "commercial@example.com", "role": "commercial"}


@pytest.fixture
def client_dto_instance():
    return ClientDTO(
        id=1,
        name="Test Client",
        email="test@example.com",
        phone="123456789",
        company="Test Company",
        creation_date=date.today(),
        last_contact_date=None,
        commercial_id=42,
    )


def test_create_client_from_input_successful(client_bl_instance, client_dal, collaborator_dal, mock_current_user):
    mock_collaborator = MagicMock(id=42, email=mock_current_user["sub"])
    collaborator_dal.get_by_email_raw.return_value = mock_collaborator
    client_dal.get_by_email.return_value = None
    client_dal.create.return_value = MagicMock(id=1)

    with patch("security.permissions.is_commercial", return_value=True):
        result = client_bl_instance.create_client_from_input(
            name="New Client",
            email="newclient@example.com",
            phone="987654321",
            company="New Company",
            current_user=mock_current_user
        )

    assert result.id == 1
    collaborator_dal.get_by_email_raw.assert_called_once_with(mock_current_user["sub"])
    client_dal.get_by_email.assert_called_once_with("newclient@example.com")
    client_dal.create.assert_called_once_with({
        "name": "New Client",
        "email": "newclient@example.com",
        "phone": "987654321",
        "company": "New Company",
        "commercial_id": 42,
        "creation_date": date.today()
    })

def test_create_client_from_input_permission_error(client_bl_instance, mock_current_user):
    with patch("bl.client_bl.is_commercial", return_value=False):
        client_bl_instance.dal.get_by_email.return_value = None
        with pytest.raises(PermissionError, match="Seuls les commerciaux peuvent créer des clients"):
            client_bl_instance.create_client_from_input(
                name="Unauthorized Client",
                email="unauthorized@example.com",
                phone=None,
                company=None,
                current_user=mock_current_user
            )


def test_create_client_from_input_missing_required_fields(client_bl_instance, mock_current_user):
    with patch("security.permissions.is_commercial", return_value=True):
        with pytest.raises(ValueError, match="Le nom et l'email sont requis."):
            client_bl_instance.create_client_from_input(
                name=None,
                email=None,
                phone=None,
                company=None,
                current_user=mock_current_user
            )


def test_create_client_from_input_email_already_exists(client_bl_instance, client_dal, mock_current_user):
    client_dal.get_by_email.return_value = MagicMock()

    with patch("security.permissions.is_commercial", return_value=True):
        with pytest.raises(ValueError, match="Un client avec cet email existe déjà."):
            client_bl_instance.create_client_from_input(
                name="Duplicate Client",
                email="duplicate@example.com",
                phone=None,
                company=None,
                current_user=mock_current_user
            )

    client_dal.get_by_email.assert_called_once_with("duplicate@example.com")


def test_create_client_from_input_collaborator_not_found(client_bl_instance, collaborator_dal, mock_current_user):
    collaborator_dal.get_by_email_raw.return_value = None
    client_bl_instance.dal.get_by_email.return_value = None

    with patch("security.permissions.is_commercial", return_value=True):
        with pytest.raises(ValueError, match="collaborateur introuvable"):
            client_bl_instance.create_client_from_input(
                name="Client Without Collaborator",
                email="nocollaborator@example.com",
                phone=None,
                company=None,
                current_user=mock_current_user
            )

    collaborator_dal.get_by_email_raw.assert_called_once_with(mock_current_user["sub"])

@pytest.fixture
def client_bl():
    fake_db = MagicMock()
    bl = ClientBLL(fake_db)
    bl.dal = MagicMock()
    bl.collaborator_dal = MagicMock()
    return bl


@patch("bl.client_bl.is_commercial", return_value=False)
def test_create_client_not_commercial(mock_perm, client_bl):
    with pytest.raises(PermissionError, match="Seuls les commerciaux peuvent créer des clients"):
        client_bl.create_client_from_input("Alice", "alice@example.com",
                                           "0102030405", "ACorp", {"sub": "x"})


@patch("bl.client_bl.is_commercial", return_value=True)
def test_create_client_missing_name_or_email(mock_perm, client_bl):
    with pytest.raises(ValueError, match="Le nom et l'email sont requis."):
        client_bl.create_client_from_input("", "alice@example.com",
                                           "0102030405", "ACorp", {"sub": "x"})

    with pytest.raises(ValueError, match="Le nom et l'email sont requis."):
        client_bl.create_client_from_input("Alice", "",
                                           "0102030405", "ACorp", {"sub": "x"})


@patch("bl.client_bl.is_commercial", return_value=True)
def test_create_client_email_already_exists(mock_perm, client_bl):
    client_bl.dal.get_by_email.return_value = MagicMock()
    with pytest.raises(ValueError, match="Un client avec cet email existe déjà."):
        client_bl.create_client_from_input("Alice", "alice@example.com",
                                           "0102030405", "ACorp", {"sub": "x"})


@patch("bl.client_bl.is_commercial", return_value=True)
def test_create_client_collaborator_not_found(mock_perm, client_bl):
    client_bl.dal.get_by_email.return_value = None
    client_bl.collaborator_dal.get_by_email_raw.return_value = None

    with pytest.raises(ValueError, match="collaborateur introuvable"):
        client_bl.create_client_from_input("Alice", "alice@example.com",
                                           "0102030405", "ACorp", {"sub": "x"})


@patch("bl.client_bl.is_commercial", return_value=True)
def test_create_client_integrity_error(mock_perm, client_bl):
    # Arrange
    client_bl.dal.get_by_email.return_value = None
    fake_collab = MagicMock()
    fake_collab.id = 42
    client_bl.collaborator_dal.get_by_email_raw.return_value = fake_collab
    client_bl.dal.create.side_effect = IntegrityError("INSERT", {}, Exception("duplicate"))

    # Act + Assert
    with pytest.raises(ValueError, match="Email client déja utilisé."):
        client_bl.create_client_from_input("Alice", "alice@example.com",
                                           "0102030405", "ACorp", {"sub": "x"})


@patch("bl.client_bl.is_commercial", return_value=True)
def test_create_client_unexpected_exception(mock_perm, client_bl):
    # Arrange
    client_bl.dal.get_by_email.return_value = None
    fake_collab = MagicMock()
    fake_collab.id = 42
    client_bl.collaborator_dal.get_by_email_raw.return_value = fake_collab
    client_bl.dal.create.side_effect = Exception("oops")

    # Act + Assert
    with pytest.raises(ValueError, match="Une erreur inattendue est survenue : oops"):
        client_bl.create_client_from_input("Alice", "alice@example.com",
                                           "0102030405", "ACorp", {"sub": "x"})
