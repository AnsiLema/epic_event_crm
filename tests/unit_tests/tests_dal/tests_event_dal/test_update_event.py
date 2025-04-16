from unittest.mock import MagicMock

import pytest
from dal.event_dal import EventDAL
from dtos.event_dto import EventDTO
from models.event import Event
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def event_dal(mock_session):
    return EventDAL(mock_session)


@pytest.fixture
def sample_event():
    return Event(
        id=1,
        start_date="2023-10-01 10:00:00",
        end_date="2023-10-01 12:00:00",
        location="Conference Room A",
        attendees=10,
        note="Monthly meeting",
        contract_id=100,
        support_id=200
    )


def test_update_updates_event_properties(event_dal, mock_session, sample_event):
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None
    event_dal._to_dto = MagicMock(return_value=EventDTO(
        id=1,
        start_date="2023-10-01 10:00:00",
        end_date="2023-10-01 12:00:00",
        location="Updated Conference Room A",
        attendees=20,
        note="Updated note",
        contract_id=100,
        support_id=200
    ))
    updates = {
        "location": "Updated Conference Room A",
        "attendees": 20,
        "note": "Updated note"
    }

    updated_event = event_dal.update(sample_event, updates)

    assert sample_event.location == "Updated Conference Room A"
    assert sample_event.attendees == 20
    assert sample_event.note == "Updated note"
    assert updated_event.location == "Updated Conference Room A"
    assert updated_event.attendees == 20
    assert updated_event.note == "Updated note"


def test_update_commits_and_refreshes(event_dal, mock_session, sample_event):
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None
    event_dal._to_dto = MagicMock(return_value=EventDTO(
        id=1,
        start_date="2023-10-01 10:00:00",
        end_date="2023-10-01 12:00:00",
        location="Updated Conference Room A",
        attendees=20,
        note="Updated note",
        contract_id=100,
        support_id=200
    ))
    updates = {
        "location": "Updated Conference Room A",
        "attendees": 20,
        "note": "Updated note"
    }

    event_dal.update(sample_event, updates)

    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(sample_event)


def test_update_returns_updated_event_dto(event_dal, mock_session, sample_event):
    event_dal._to_dto = MagicMock(return_value=EventDTO(
        id=1,
        start_date="2023-10-01 10:00:00",
        end_date="2023-10-01 12:00:00",
        location="Updated Conference Room A",
        attendees=20,
        note="Updated note",
        contract_id=100,
        support_id=200
    ))
    updates = {
        "location": "Updated Conference Room A",
        "attendees": 20,
        "note": "Updated note"
    }

    updated_event = event_dal.update(sample_event, updates)

    assert updated_event.id == 1
    assert updated_event.location == "Updated Conference Room A"
    assert updated_event.attendees == 20
    assert updated_event.note == "Updated note"
    assert updated_event.contract_id == 100
    assert updated_event.support_id == 200
