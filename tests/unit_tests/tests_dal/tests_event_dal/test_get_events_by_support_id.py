from unittest.mock import MagicMock

import pytest
from dal.event_dal import EventDAL
from dtos.event_dto import EventDTO
from models.event import Event


def test_get_by_support_id_returns_events(mocker):
    mock_db_session = MagicMock()
    mock_event = MagicMock(spec=Event)
    mock_event_dto = EventDTO(
        id=1,
        start_date="2023-10-01T10:00:00",
        end_date="2023-10-01T12:00:00",
        location="Conference Room A",
        attendees=20,
        note="Important event",
        contract_id=101,
        support_id=10,
    )

    mock_event_dal = EventDAL(mock_db_session)

    # Mock the internal method _to_dto
    mocker.patch.object(mock_event_dal, "_to_dto", return_value=mock_event_dto)

    # Mock the database query
    mock_db_session.query.return_value.filter_by.return_value.all.return_value = [mock_event]

    result = mock_event_dal.get_by_support_id(10)

    assert len(result) == 1
    assert isinstance(result[0], EventDTO)
    assert result[0].id == 1
    assert result[0].support_id == 10


def test_get_by_support_id_returns_empty_list(mocker):
    mock_db_session = MagicMock()
    mock_event_dal = EventDAL(mock_db_session)

    # Mock the database query to return no events
    mock_db_session.query.return_value.filter_by.return_value.all.return_value = []

    result = mock_event_dal.get_by_support_id(999)

    assert len(result) == 0
