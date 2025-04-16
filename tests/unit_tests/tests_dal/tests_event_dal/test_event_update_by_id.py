from unittest.mock import Mock

import pytest
from dal.event_dal import EventDAL
from dtos.event_dto import EventDTO
from models.event import Event
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    return Mock(spec=Session)


@pytest.fixture
def event_dal(mock_session):
    return EventDAL(db=mock_session)


@pytest.fixture
def mock_event():
    return Event(
        id=1,
        start_date="2023-10-01 10:00:00",
        end_date="2023-10-01 12:00:00",
        location="Conference Room A",
        attendees=50,
        note="Quarterly meeting",
        contract_id=101,
        support_id=None
    )


@pytest.fixture
def mock_event_dto():
    return EventDTO(
        id=1,
        start_date="2023-10-01 10:00:00",
        end_date="2023-10-01 12:00:00",
        location="Conference Room A",
        attendees=50,
        note="Quarterly meeting",
        contract_id=101,
        support_id=None
    )


def test_update_by_id_event_found(mocker, event_dal, mock_session, mock_event, mock_event_dto):
    # Arrange
    mock_query = mock_session.query.return_value
    mock_query.filter_by.return_value.first.return_value = mock_event

    mocker.patch.object(event_dal, 'update', return_value=mock_event_dto)

    updates = {"note": "Updated meeting details"}

    # Act
    result = event_dal.update_by_id(event_id=1, updates=updates)

    # Assert
    assert result == mock_event_dto
    mock_query.filter_by.assert_any_call(id=1)
    event_dal.update.assert_called_once_with(mock_event, updates)


def test_update_by_id_event_not_found(event_dal, mock_session):
    # Arrange
    mock_query = mock_session.query.return_value
    mock_query.filter_by.return_value.first.return_value = None

    updates = {"note": "Updated meeting details"}

    # Act
    result = event_dal.update_by_id(event_id=1, updates=updates)

    # Assert
    assert result is None
    mock_query.filter_by.assert_any_call(id=1)


def test_update_by_id_empty_updates(mocker, event_dal, mock_session, mock_event, mock_event_dto):
    # Arrange
    mock_query = mock_session.query.return_value
    mock_query.filter_by.return_value.first.return_value = mock_event

    mocker.patch.object(event_dal, 'update', return_value=mock_event_dto)

    updates = {}

    # Act
    result = event_dal.update_by_id(event_id=1, updates=updates)

    # Assert
    assert result == mock_event_dto
    mock_query.filter_by.assert_any_call(id=1)
    event_dal.update.assert_called_once_with(mock_event, updates)
