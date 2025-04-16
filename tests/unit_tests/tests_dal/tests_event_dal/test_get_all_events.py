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


def test_get_all_returns_empty_list(event_dal, mock_session):
    mock_session.query.return_value.all.return_value = []
    result = event_dal.get_all()
    assert result == []


def test_get_all_returns_event_dto_list(event_dal, mock_session):
    event_1 = Event(
        id=1,
        start_date="2023-11-01 10:00:00",
        end_date="2023-11-01 12:00:00",
        location="Venue A",
        attendees=50,
        note=None,
        contract_id=101,
        support_id=201,
    )
    event_2 = Event(
        id=2,
        start_date="2023-11-02 14:00:00",
        end_date="2023-11-02 16:00:00",
        location="Venue B",
        attendees=30,
        note="Important event",
        contract_id=102,
        support_id=202,
    )

    mock_session.query.return_value.all.return_value = [event_1, event_2]

    event_dal._to_dto = MagicMock(side_effect=[
        EventDTO(
            id=1,
            start_date="2023-11-01 10:00:00",
            end_date="2023-11-01 12:00:00",
            location="Venue A",
            attendees=50,
            note=None,
            contract_id=101,
            support_id=201,
        ),
        EventDTO(
            id=2,
            start_date="2023-11-02 14:00:00",
            end_date="2023-11-02 16:00:00",
            location="Venue B",
            attendees=30,
            note="Important event",
            contract_id=102,
            support_id=202,
        ),
    ])

    result = event_dal.get_all()

    assert len(result) == 2
    assert isinstance(result[0], EventDTO)
    assert result[0].id == 1
    assert result[0].location == "Venue A"
    assert result[1].id == 2
    assert result[1].location == "Venue B"
