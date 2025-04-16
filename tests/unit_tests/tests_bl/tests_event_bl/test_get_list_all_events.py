from unittest.mock import MagicMock

import pytest
from bl.event_bl import EventBL
from dal.event_dal import EventDAL
from dtos.event_dto import EventDTO
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def event_bl(mock_db):
    return EventBL(mock_db)


@pytest.fixture
def mock_event_dal():
    return MagicMock(spec=EventDAL)


@pytest.fixture
def mock_events():
    return [
        EventDTO(id=1, start_date="2023-01-01", end_date="2023-01-02", location="Location A", attendees=100,
                 note="Note 1", contract_id=1, support_id=None),
        EventDTO(id=2, start_date="2023-01-10", end_date="2023-01-11", location="Location B", attendees=50,
                 note="Note 2", contract_id=2, support_id=2)
    ]


def test_list_all_events(event_bl, mock_event_dal, mock_events):
    """Test the `list_all_events` method returns all events."""
    event_bl.dal = mock_event_dal
    mock_event_dal.get_all.return_value = mock_events

    result = event_bl.list_all_events()

    assert result == mock_events
    mock_event_dal.get_all.assert_called_once()


def test_list_all_events_empty(event_bl, mock_event_dal):
    """Test the `list_all_events` method when there are no events."""
    event_bl.dal = mock_event_dal
    mock_event_dal.get_all.return_value = []

    result = event_bl.list_all_events()

    assert result == []
    mock_event_dal.get_all.assert_called_once()
