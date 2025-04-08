
from datetime import datetime
from dal.event_dal import EventDAL
from models.event import Event
from sqlalchemy.orm import Session
from unittest.mock import MagicMock


def fake_event_instance():
    return Event(
        id=1,
        start_date=datetime(2024, 1, 1, 10, 0),
        end_date=datetime(2024, 1, 1, 12, 0),
        location="Paris",
        attendees=50,
        note="Test event",
        contract_id=101,
        support_id=None,
    )


def test_get_event_by_id():
    db = MagicMock(spec=Session)
    db.query().filter_by().first.return_value = fake_event_instance()

    dal = EventDAL(db)
    result = dal.get(1)

    assert result.id == 1
    assert result.location == "Paris"
    assert result.contract_id == 101


def test_get_events_without_support():
    db = MagicMock(spec=Session)
    db.query().filter_by().all.return_value = [fake_event_instance()]

    dal = EventDAL(db)
    result = dal.get_without_support()

    assert len(result) == 1
    assert result[0].support_id is None


def test_get_events_by_support_id():
    event = fake_event_instance()
    event.support_id = 42

    db = MagicMock(spec=Session)
    db.query().filter_by().all.return_value = [event]

    dal = EventDAL(db)
    result = dal.get_by_support_id(42)

    assert len(result) == 1
    assert result[0].support_id == 42