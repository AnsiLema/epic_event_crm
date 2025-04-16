from unittest.mock import MagicMock, patch

import pytest
from bl.event_bl import EventBL
from dal.collaborator_dal import CollaboratorDAL
from dal.contract_dal import ContractDAL
from dal.event_dal import EventDAL
from dtos.event_dto import EventDTO
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def event_bl(mock_session):
    return EventBL(mock_session)


@pytest.fixture
def current_user_commercial():
    return {"sub": "test@example.com", "role": "commercial"}


@pytest.fixture
def current_user_non_commercial():
    return {"sub": "test@example.com", "role": "support"}


def test_create_event_as_commercial(event_bl, current_user_commercial):
    """Test creating an event as a valid commercial user."""
    contract_dal = MagicMock(spec=ContractDAL)
    collaborator_dal = MagicMock(spec=CollaboratorDAL)
    event_dal = MagicMock(spec=EventDAL)

    event_bl.contract_dal = contract_dal
    event_bl.collaborator_dal = collaborator_dal
    event_bl.dal = event_dal

    contract_dal.get.return_value = MagicMock(status=True, commercial_id=1)
    collaborator_dal.get_by_email_raw.return_value = MagicMock(id=1)
    event_dal.create.return_value = MagicMock(spec=EventDTO, id=1)

    event_data = {
        "contract_id": 1,
        "start_date": "2023-11-01",
        "end_date": "2023-11-02"
    }

    result = event_bl.create_event(event_data, current_user_commercial)

    assert result.id == 1
    contract_dal.get.assert_called_once_with(1)
    collaborator_dal.get_by_email_raw.assert_called_once_with("test@example.com")
    event_dal.create.assert_called_once_with(event_data)


def test_create_event_as_non_commercial(event_bl, current_user_non_commercial):
    """Test creating an event as a non-commercial user raises PermissionError."""
    event_data = {
        "contract_id": 1,
        "start_date": "2023-11-01",
        "end_date": "2023-11-02"
    }

    with pytest.raises(PermissionError, match="Seuls les commerciaux peuvent créer un évènements"):
        event_bl.create_event(event_data, current_user_non_commercial)


def test_create_event_with_invalid_contract(event_bl, current_user_commercial):
    """Test creating an event with an invalid/unavailable contract raises ValueError."""
    contract_dal = MagicMock(spec=ContractDAL)
    event_bl.contract_dal = contract_dal
    contract_dal.get.return_value = None

    event_data = {
        "contract_id": 1,
        "start_date": "2023-11-01",
        "end_date": "2023-11-02"
    }

    with pytest.raises(ValueError, match="Le contrat introuvable."):
        event_bl.create_event(event_data, current_user_commercial)

    contract_dal.get.assert_called_once_with(1)


def test_create_event_with_unsigned_contract(event_bl, current_user_commercial):
    """Test creating an event with an unsigned contract raises PermissionError."""
    contract_dal = MagicMock(spec=ContractDAL)
    event_bl.contract_dal = contract_dal
    contract_dal.get.return_value = MagicMock(status=False)

    event_data = {
        "contract_id": 1,
        "start_date": "2023-11-01",
        "end_date": "2023-11-02"
    }

    with pytest.raises(PermissionError, match="Impossible de créer un évènement pour un contrat non signé."):
        event_bl.create_event(event_data, current_user_commercial)

    contract_dal.get.assert_called_once_with(1)


def test_create_event_for_unowned_contract(event_bl, current_user_commercial):
    """Test creating an event for a contract not owned by the commercial raises PermissionError."""
    contract_dal = MagicMock(spec=ContractDAL)
    collaborator_dal = MagicMock(spec=CollaboratorDAL)
    event_bl.contract_dal = contract_dal
    event_bl.collaborator_dal = collaborator_dal

    contract_dal.get.return_value = MagicMock(status=True, commercial_id=2)
    collaborator_dal.get_by_email_raw.return_value = MagicMock(id=1)

    event_data = {
        "contract_id": 1,
        "start_date": "2023-11-01",
        "end_date": "2023-11-02"
    }

    with pytest.raises(PermissionError, match="Vous ne pouvez créer un évènement que pour vos propres contrats."):
        event_bl.create_event(event_data, current_user_commercial)

    contract_dal.get.assert_called_once_with(1)
    collaborator_dal.get_by_email_raw.assert_called_once_with("test@example.com")
