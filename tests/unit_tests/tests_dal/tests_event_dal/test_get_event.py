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


def test_get_event_found(event_dal, mock_session):
    mock_event = Event(
        id=1,
        start_date="2023-12-01T12:00:00",
        end_date="2023-12-01T14:00:00",
        location="Conference Room",
        attendees=10,
        note="Meeting",
        contract_id=100,
        support_id=200,
    )
    mock_session.query().filter_by().first.return_value = mock_event
    expected_dto = EventDTO(
        id=1,
        start_date="2023-12-01T12:00:00",
        end_date="2023-12-01T14:00:00",
        location="Conference Room",
        attendees=10,
        note="Meeting",
        contract_id=100,
        support_id=200,
    )
    event_dal._to_dto = MagicMock(return_value=expected_dto)

    result = event_dal.get(1)

    assert result == expected_dto
    event_dal._to_dto.assert_called_once_with(mock_event)


def test_get_event_not_found(event_dal, mock_session):
    mock_session.query().filter_by().first.return_value = None

    result = event_dal.get(1)

    assert result is None
    mock_session.query().filter_by().first.assert_called_once()
