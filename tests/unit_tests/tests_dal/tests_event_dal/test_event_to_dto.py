import pytest
from dal.event_dal import EventDAL
from dtos.event_dto import EventDTO
from models.event import Event


def test_to_dto_with_full_event():
    event = Event(
        id=1,
        start_date="2023-12-01T10:00:00",
        end_date="2023-12-01T12:00:00",
        location="New York",
        attendees=50,
        note="Annual meeting",
        contract_id=10,
        support_id=5
    )
    event_dal = EventDAL(None)
    result = event_dal._to_dto(event)

    assert isinstance(result, EventDTO)
    assert result.id == event.id
    assert result.start_date == event.start_date
    assert result.end_date == event.end_date
    assert result.location == event.location
    assert result.attendees == event.attendees
    assert result.note == event.note
    assert result.contract_id == event.contract_id
    assert result.support_id == event.support_id


def test_to_dto_with_minimal_event():
    event = Event(
        id=2,
        start_date="2023-12-15T10:00:00",
        end_date="2023-12-15T11:00:00",
        location=None,
        attendees=10,
        note=None,
        contract_id=12,
        support_id=None
    )
    event_dal = EventDAL(None)
    result = event_dal._to_dto(event)

    assert isinstance(result, EventDTO)
    assert result.id == event.id
    assert result.start_date == event.start_date
    assert result.end_date == event.end_date
    assert result.location == event.location
    assert result.attendees == event.attendees
    assert result.note == event.note
    assert result.contract_id == event.contract_id
    assert result.support_id == event.support_id
