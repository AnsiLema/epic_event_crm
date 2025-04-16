import pytest
from dal.event_dal import EventDAL
from dtos.event_dto import EventDTO
from models.event import Event
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session(mocker):
    return mocker.MagicMock(spec=Session)


@pytest.fixture
def event_dal(mock_session):
    return EventDAL(db=mock_session)


@pytest.fixture
def mock_events():
    return [
        Event(id=1, start_date="2023-12-01", end_date="2023-12-10", location="Venue A", attendees=100, note=None,
              contract_id=1, support_id=None),
        Event(id=2, start_date="2023-12-05", end_date="2023-12-15", location="Venue B", attendees=50,
              note="Special event", contract_id=2, support_id=None)
    ]


def test_get_without_support_returns_correct_dto(event_dal, mock_session, mock_events, mocker):
    mock_session.query.return_value.filter_by.return_value.all.return_value = mock_events
    mocked_to_dto = mocker.patch.object(event_dal, '_to_dto', side_effect=lambda e: EventDTO(
        id=e.id,
        start_date=e.start_date,
        end_date=e.end_date,
        location=e.location,
        attendees=e.attendees,
        note=e.note,
        contract_id=e.contract_id,
        support_id=e.support_id
    ))

    result = event_dal.get_without_support()

    assert len(result) == len(mock_events)
    for dto, event in zip(result, mock_events):
        mocked_to_dto.assert_any_call(event)
        assert dto.id == event.id
        assert dto.start_date == event.start_date
        assert dto.end_date == event.end_date
        assert dto.location == event.location
        assert dto.attendees == event.attendees
        assert dto.note == event.note
        assert dto.contract_id == event.contract_id
        assert dto.support_id == event.support_id


def test_get_without_support_no_events(event_dal, mock_session):
    mock_session.query.return_value.filter_by.return_value.all.return_value = []

    result = event_dal.get_without_support()

    assert result == []
