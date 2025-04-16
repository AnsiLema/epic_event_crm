from unittest.mock import MagicMock, patch

import pytest
from bl.event_bl import EventBL
from dal.collaborator_dal import CollaboratorDAL
from dal.event_dal import EventDAL
from dtos.event_dto import EventDTO
from security.permissions import can_manage_events, is_support
from sqlalchemy.orm import Session


@pytest.fixture
def db_session():
    """Fixture to provide a mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def event_dal(db_session):
    """Fixture to provide a mocked EventDAL."""
    return MagicMock(spec=EventDAL)


@pytest.fixture
def collaborator_dal(db_session):
    """Fixture to provide a mocked CollaboratorDAL."""
    return MagicMock(spec=CollaboratorDAL)


@pytest.fixture
def event_bl(db_session, event_dal, collaborator_dal):
    """Fixture to initialize EventBL with mock dependencies."""
    bl = EventBL(db_session)
    bl.dal = event_dal
    bl.collaborator_dal = collaborator_dal
    return bl


def test_update_event_success_management_role(event_bl, event_dal):
    """Test update_event with a management role."""
    event_id = 1
    updates = {"location": "New Location"}
    current_user = {"role": "gestion"}
    updated_event = EventDTO(
        id=event_id, start_date=None, end_date=None, location="New Location",
        attendees=50, note=None, contract_id=1, support_id=None
    )

    with patch("bl.event_bl.can_manage_events", return_value=True):
        event_dal.get.return_value = updated_event
        event_dal.update_by_id.return_value = updated_event

        result = event_bl.update_event(event_id, updates, current_user)

        assert result == updated_event
        event_dal.get.assert_called_once_with(event_id)
        event_dal.update_by_id.assert_called_once_with(event_id, updates)


@patch("bl.event_bl.is_support", return_value=True)
@patch("bl.event_bl.can_manage_events", return_value=False)
def test_update_event_success_support_role(mock_manage, mock_support, event_bl, event_dal, collaborator_dal):
    """Test update_event with a support role updating its own event."""
    event_id = 2
    updates = {"attendees": 100}
    current_user = {"sub": "user@example.com", "role": "support"}
    user_id = 5

    mock_event = EventDTO(
        id=event_id, start_date=None, end_date=None, location="Location A",
        attendees=50, note=None, contract_id=1, support_id=user_id
    )
    updated_event = EventDTO(
        id=event_id, start_date=None, end_date=None, location="Location A",
        attendees=100, note=None, contract_id=1, support_id=user_id
    )

    event_dal.get.return_value = mock_event

    collaborator_mock = MagicMock()
    collaborator_mock.id = user_id
    collaborator_dal.get_by_email_raw.return_value = collaborator_mock

    event_dal.update_by_id.return_value = updated_event

    result = event_bl.update_event(event_id, updates, current_user)

    assert result == updated_event
    event_dal.get.assert_called_once_with(event_id)
    collaborator_dal.get_by_email_raw.assert_called_once_with(current_user["sub"])


def test_update_event_failure_event_not_found(event_bl, event_dal):
    """Test update_event when event is not found."""
    event_id = 10
    updates = {"location": "Unknown"}
    current_user = {"role": "gestion"}

    event_dal.get.return_value = None

    with pytest.raises(ValueError, match="Évènement introuvable."):
        event_bl.update_event(event_id, updates, current_user)

    event_dal.get.assert_called_once_with(event_id)


def test_update_event_failure_unauthorized_support(event_bl, event_dal, collaborator_dal):
    """Test update_event when support tries to update non-assigned event."""
    event_id = 3
    updates = {"attendees": 150}
    current_user = {"sub": "user@example.com", "role": "support"}
    user_id = 7

    mock_event = EventDTO(
        id=event_id,
        start_date=None,
        end_date=None,
        location="Location B",
        attendees=50,
        note=None,
        contract_id=2,
        support_id=10  # ≠ user_id
    )

    with patch("bl.event_bl.is_support", return_value=True), \
         patch("bl.event_bl.can_manage_events", return_value=False):

        event_dal.get.return_value = mock_event

        collaborator_mock = MagicMock()
        collaborator_mock.id = user_id
        collaborator_dal.get_by_email_raw.return_value = collaborator_mock

        with pytest.raises(PermissionError, match="Vous ne pouvez modifier que les événements qui vous sont attribués."):
            event_bl.update_event(event_id, updates, current_user)


def test_update_event_failure_no_permission(event_bl, event_dal):
    """Test update_event when user has no permissions."""
    event_id = 4
    updates = {"note": "Updated note"}
    current_user = {"role": "viewer"}

    with patch("bl.event_bl.can_manage_events", return_value=False), \
            patch("bl.event_bl.is_support", return_value=False):
        with pytest.raises(PermissionError, match="Vous n'avez pas les droits pour modifier cet évènement."):
            event_bl.update_event(event_id, updates, current_user)

        event_dal.get.assert_called_once_with(event_id)
