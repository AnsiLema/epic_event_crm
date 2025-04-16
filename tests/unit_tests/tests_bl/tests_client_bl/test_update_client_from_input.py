from unittest.mock import MagicMock, patch
import pytest
from bl.client_bl import ClientBLL
from dtos.client_dto import ClientDTO
from sqlalchemy.orm import Session


@pytest.fixture
def mock_client_dal():
    return MagicMock()


@pytest.fixture
def mock_collaborator_dal():
    return MagicMock()


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def client_bll(mock_client_dal, mock_collaborator_dal, db_session):
    bll = ClientBLL(db_session)
    bll.dal = mock_client_dal
    bll.collaborator_dal = mock_collaborator_dal
    return bll


@pytest.fixture
def valid_client_dto():
    return ClientDTO(
        id=1,
        name="Test Client",
        email="test@example.com",
        phone="123-456-7890",
        company="Test Company",
        creation_date="2023-01-01",
        last_contact_date=None,
        commercial_id=1,
    )


@pytest.fixture
def valid_collaborator():
    return MagicMock(id=1, email="commercial@example.com")


def test_update_client_from_input_success(
        client_bll, mock_client_dal, mock_collaborator_dal, valid_client_dto, valid_collaborator
):
    mock_collaborator_dal.get_by_email_raw.return_value = valid_collaborator
    mock_client_dal.get.return_value = valid_client_dto
    mock_client_dal.update_by_id.return_value = valid_client_dto

    result = client_bll.update_client_from_input(
        client_id=1,
        name="Updated Client",
        email="updated@example.com",
        phone="555-444-3333",
        company="Updated Company",
        current_user={"sub": "commercial@example.com", "role": "commercial"},
    )

    assert result == valid_client_dto
    mock_collaborator_dal.get_by_email_raw.assert_called_once_with("commercial@example.com")
    mock_client_dal.get.assert_called_once_with(1)
    mock_client_dal.update_by_id.assert_called_once_with(
        1, {"name": "Updated Client", "email": "updated@example.com", "phone": "555-444-3333",
            "company": "Updated Company"}
    )


def test_update_client_from_input_permission_error(client_bll):
    with pytest.raises(PermissionError, match="Seuls les commerciaux peuvent modifier un client"):
        client_bll.update_client_from_input(
            client_id=1,
            name="Updated Client",
            email="updated@example.com",
            phone="555-444-3333",
            company="Updated Company",
            current_user={"sub": "unauthorized@example.com", "role": "other"},
        )


def test_update_client_from_input_client_not_found(
        client_bll, mock_client_dal, mock_collaborator_dal, valid_collaborator
):
    mock_collaborator_dal.get_by_email_raw.return_value = valid_collaborator
    mock_client_dal.get.return_value = None

    with pytest.raises(ValueError, match="client introuvable"):
        client_bll.update_client_from_input(
            client_id=99,
            name="Updated Client",
            email="updated@example.com",
            phone="555-444-3333",
            company="Updated Company",
            current_user={"sub": "commercial@example.com", "role": "commercial"},
        )


def test_update_client_from_input_collaborator_not_found(client_bll, mock_collaborator_dal):
    mock_collaborator_dal.get_by_email_raw.return_value = None

    with pytest.raises(ValueError, match="collaborateur introuvable"):
        client_bll.update_client_from_input(
            client_id=1,
            name="Updated Client",
            email="updated@example.com",
            phone="555-444-3333",
            company="Updated Company",
            current_user={"sub": "unknown@example.com", "role": "commercial"},
        )


def test_update_client_from_input_not_own_client(
        client_bll, mock_client_dal, mock_collaborator_dal, valid_client_dto, valid_collaborator
):
    valid_client_dto.commercial_id = 2
    mock_collaborator_dal.get_by_email_raw.return_value = valid_collaborator
    mock_client_dal.get.return_value = valid_client_dto

    with pytest.raises(PermissionError, match="Vous ne pouvez modifier que vos propres clients."):
        client_bll.update_client_from_input(
            client_id=1,
            name="Updated Client",
            email="updated@example.com",
            phone="555-444-3333",
            company="Updated Company",
            current_user={"sub": "commercial@example.com", "role": "commercial"},
        )

@pytest.fixture
def client_bl():
    fake_db = MagicMock()
    bl = ClientBLL(fake_db)
    bl.dal = MagicMock()
    bl.collaborator_dal = MagicMock()
    return bl


@patch("bl.client_bl.is_commercial", return_value=True)
def test_update_client_success(mock_is_commercial, client_bl):
    current_user = {"sub": "com@ex.com", "role": "commercial"}
    collaborator = MagicMock(id=1)
    client = MagicMock(commercial_id=1)
    client_bl.collaborator_dal.get_by_email_raw.return_value = collaborator
    client_bl.dal.get.return_value = client

    updated_dto = ClientDTO(
        id=123,
        name="New Name",
        email="new@example.com",
        phone="0123456789",
        company="NewCorp",
        commercial_id=1,
        creation_date=client.creation_date,
        last_contact_date=client.last_contact_date
    )
    client_bl.dal.update_by_id.return_value = updated_dto

    result = client_bl.update_client_from_input(
        client_id=123,
        name="New Name",
        email="new@example.com",
        phone="0123456789",
        company="NewCorp",
        current_user=current_user
    )

    assert isinstance(result, ClientDTO)
    assert result.name == "New Name"
    assert result.email == "new@example.com"
    assert result.company == "NewCorp"


@patch("bl.client_bl.is_commercial", return_value=False)
def test_update_client_permission_denied_for_role(mock_is_commercial, client_bl):
    current_user = {"sub": "unauth@ex.com", "role": "support"}
    with pytest.raises(PermissionError, match="Seuls les commerciaux peuvent modifier un client"):
        client_bl.update_client_from_input(1, "Name", "email", "phone", "company", current_user)


@patch("bl.client_bl.is_commercial", return_value=True)
def test_update_client_collaborator_not_found(mock_is_commercial, client_bl):
    current_user = {"sub": "com@ex.com"}
    client_bl.collaborator_dal.get_by_email_raw.return_value = None

    with pytest.raises(ValueError, match="collaborateur introuvable"):
        client_bl.update_client_from_input(1, "Name", "email", "phone", "company", current_user)


@patch("bl.client_bl.is_commercial", return_value=True)
def test_update_client_not_found(mock_is_commercial, client_bl):
    current_user = {"sub": "com@ex.com"}
    collaborator = MagicMock(id=1)
    client_bl.collaborator_dal.get_by_email_raw.return_value = collaborator
    client_bl.dal.get.return_value = None

    with pytest.raises(ValueError, match="client introuvable"):
        client_bl.update_client_from_input(1, "Name", "email", "phone", "company", current_user)


@patch("bl.client_bl.is_commercial", return_value=True)
def test_update_client_not_owned(mock_is_commercial, client_bl):
    current_user = {"sub": "com@ex.com"}
    collaborator = MagicMock(id=1)
    other_client = MagicMock(commercial_id=2)
    client_bl.collaborator_dal.get_by_email_raw.return_value = collaborator
    client_bl.dal.get.return_value = other_client

    with pytest.raises(PermissionError, match="Vous ne pouvez modifier que vos propres clients."):
        client_bl.update_client_from_input(1, "Name", "email", "phone", "company", current_user)