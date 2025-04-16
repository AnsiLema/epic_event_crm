import pytest
from dal.event_dal import EventDAL
from dtos.event_dto import EventDTO
from models.event import Event
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def db_session(mocker):
    return MagicMock(spec=Session)


@pytest.fixture
def event_dal(db_session):
    return EventDAL(db_session)


@pytest.fixture
def sample_event_data():
    return {
        "start_date": "2023-10-01T10:00:00",
        "end_date": "2023-10-01T12:00:00",
        "location": "Conference Room A",
        "attendees": 50,
        "note": "Important meeting",
        "contract_id": 1,
        "support_id": 2,
    }


@pytest.fixture
def sample_event():
    return Event(
        id=1,
        start_date="2023-10-01T10:00:00",
        end_date="2023-10-01T12:00:00",
        location="Conference Room A",
        attendees=50,
        note="Important meeting",
        contract_id=1,
        support_id=2,
    )


@pytest.fixture
def sample_event_dto():
    return EventDTO(
        id=1,
        start_date="2023-10-01T10:00:00",
        end_date="2023-10-01T12:00:00",
        location="Conference Room A",
        attendees=50,
        note="Important meeting",
        contract_id=1,
        support_id=2,
    )

def test_create_event(event_dal, db_session, sample_event_data, sample_event_dto, mocker):
    # Arrange
    mocker.patch.object(event_dal, "_to_dto", return_value=sample_event_dto)
    db_session.refresh.side_effect = lambda obj: None  # Evite erreur si accède à l'objet
    db_session.add.reset_mock()
    db_session.commit.reset_mock()

    # Act
    result = event_dal.create(sample_event_data)

    # Assert
    assert db_session.add.call_count == 1
    added_event = db_session.add.call_args.args[0]
    assert isinstance(added_event, Event)
    assert added_event.location == sample_event_data["location"]

    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(added_event)
    event_dal._to_dto.assert_called_once_with(added_event)
    assert result == sample_event_dto


def test_create_event_invalid_data_commit_error(event_dal, db_session, mocker):
    # Incomplete but valid data on the Python side
    invalid_data = {
        "start_date": "2023-10-01T10:00:00",
        "end_date": "2023-10-01T12:00:00",
        "location": "Conference Room A",
        # Missing contract_id, which is NOT NULL
    }

    db_session.commit.side_effect = IntegrityError("INSERT", {}, Exception("NOT NULL violation"))

    with pytest.raises(IntegrityError):
        event_dal.create(invalid_data)