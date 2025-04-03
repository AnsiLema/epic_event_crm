from datetime import datetime
from unittest.mock import MagicMock

import pytest
from models.collaborator import Collaborator
from models.contract import Contract
from services.event_service import create_event
from sqlalchemy.orm import Session



@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_payload():
    return {"sub": "test@example.com", "role": "commercial"}


@pytest.fixture
def mock_contract():
    contract = Contract(id=1, status=True)
    contract.client = MagicMock(commercial_id=1)
    return contract


@pytest.fixture
def mock_commercial():
    return Collaborator(id=1, email="test@example.com")


def test_create_event_success(mock_session, mock_payload, mock_contract, mock_commercial):
    mock_session.query().filter_by().first.side_effect = [mock_commercial, mock_contract]

    start_date = datetime(2023, 11, 1, 10, 0)
    end_date = datetime(2023, 11, 1, 12, 0)
    location = "Test Location"
    attendees = "100"
    note = "Test note"

    event = create_event(
        db=mock_session,
        payload=mock_payload,
        contract_id=1,
        start_date=start_date,
        end_date=end_date,
        location=location,
        attendees=attendees,
        note=note,
    )

    assert event is not None
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(event)
    assert event.start_date == start_date
    assert event.end_date == end_date
    assert event.location == location
    assert event.attendees == attendees
    assert event.note == note
    assert event.contract == mock_contract


def test_create_event_non_commercial_user(mock_session, mock_payload):
    mock_payload["role"] = "non-commercial"

    event = create_event(
        db=mock_session,
        payload=mock_payload,
        contract_id=1,
        start_date=datetime(2023, 11, 1, 10, 0),
        end_date=datetime(2023, 11, 1, 12, 0),
        location="Test Location",
        attendees="100",
    )

    assert event is None
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


def test_create_event_commercial_not_found(mock_session, mock_payload):
    mock_session.query().filter_by().first.return_value = None

    event = create_event(
        db=mock_session,
        payload=mock_payload,
        contract_id=1,
        start_date=datetime(2023, 11, 1, 10, 0),
        end_date=datetime(2023, 11, 1, 12, 0),
        location="Test Location",
        attendees="100",
    )

    assert event is None
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


def test_create_event_contract_not_found(mock_session, mock_payload, mock_commercial):
    mock_session.query().filter_by().first.side_effect = [mock_commercial, None]

    event = create_event(
        db=mock_session,
        payload=mock_payload,
        contract_id=1,
        start_date=datetime(2023, 11, 1, 10, 0),
        end_date=datetime(2023, 11, 1, 12, 0),
        location="Test Location",
        attendees="100",
    )

    assert event is None
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


def test_create_event_unsigned_contract(mock_session, mock_payload, mock_commercial):
    mock_contract = Contract(id=1, status=False)
    mock_contract.client = MagicMock(commercial_id=1)
    mock_session.query().filter_by().first.side_effect = [mock_commercial, mock_contract]

    event = create_event(
        db=mock_session,
        payload=mock_payload,
        contract_id=1,
        start_date=datetime(2023, 11, 1, 10, 0),
        end_date=datetime(2023, 11, 1, 12, 0),
        location="Test Location",
        attendees="100",
    )

    assert event is None
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


def test_create_event_unauthorized_commercial(mock_session, mock_payload, mock_commercial):
    mock_contract = Contract(id=1, status=True)
    mock_contract.client = MagicMock(commercial_id=2)  # Different commercial ID
    mock_session.query().filter_by().first.side_effect = [mock_commercial, mock_contract]

    event = create_event(
        db=mock_session,
        payload=mock_payload,
        contract_id=1,
        start_date=datetime(2023, 11, 1, 10, 0),
        end_date=datetime(2023, 11, 1, 12, 0),
        location="Test Location",
        attendees="100",
    )

    assert event is None
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
