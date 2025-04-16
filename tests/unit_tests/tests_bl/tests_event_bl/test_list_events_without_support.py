from unittest.mock import MagicMock

import pytest
from bl.event_bl import EventBL
from dal.event_dal import EventDAL
from dtos.event_dto import EventDTO
from security.permissions import can_manage_events


@pytest.fixture
def mock_db():
    """Fixture to provide a mocked database session."""
    return MagicMock()


@pytest.fixture
def mock_event_dal(mock_db):
    """Fixture to provide a mocked EventDAL instance."""
    return MagicMock(spec=EventDAL, db=mock_db)


@pytest.fixture
def event_bl(mock_db, mock_event_dal):
    """Fixture to provide an EventBL instance with mocked dependencies."""
    event_bl_instance = EventBL(mock_db)
    event_bl_instance.dal = mock_event_dal
    return event_bl_instance


@pytest.fixture
def current_user_manager():
    """Fixture to represent a 'manager' user with necessary permissions."""
    return {"role": "gestion"}


@pytest.fixture
def current_user_no_access():
    """Fixture to represent a user without the necessary permissions."""
    return {"role": "other"}


def test_list_events_without_support_with_permission(event_bl, mock_event_dal, current_user_manager):
    """Test that events without support are returned when the user has permissions."""
    # Arrange
    mock_events = [
        EventDTO(id=1, start_date=None, end_date=None, location="Location 1", attendees=100,
                 note=None, contract_id=1, support_id=None),
        EventDTO(id=2, start_date=None, end_date=None, location="Location 2", attendees=200,
                 note="Event Note", contract_id=2, support_id=None),
    ]
    mock_event_dal.get_without_support.return_value = mock_events

    # Act
    result = event_bl.list_events_without_support(current_user_manager)

    # Assert
    assert result == mock_events
    mock_event_dal.get_without_support.assert_called_once()


def test_list_events_without_support_without_permission(event_bl, current_user_no_access):
    """Test that a PermissionError is raised when the user lacks permissions."""
    # Act / Assert
    with pytest.raises(PermissionError, match="Seuls les gestionnaires peuvent acceder à cette fonction."):
        event_bl.list_events_without_support(current_user_no_access)


def test_list_events_without_support_empty_result(event_bl, mock_event_dal, current_user_manager):
    """Test that an empty list is returned when no events without support exist."""
    # Arrange
    mock_event_dal.get_without_support.return_value = []

    # Act
    result = event_bl.list_events_without_support(current_user_manager)

    # Assert
    assert result == []
    mock_event_dal.get_without_support.assert_called_once()
