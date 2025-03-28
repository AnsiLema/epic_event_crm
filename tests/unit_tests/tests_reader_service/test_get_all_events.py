import pytest
from models.event import Event
from services.reader_service import get_all_events
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime


# Configure in-memory SQLite database for testing
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    Event.metadata.create_all(engine)
    try:
        yield session
    finally:
        session.close()
        Event.metadata.drop_all(engine)


def test_get_all_events_returns_empty_list_when_no_events_exist(db_session):
    result = get_all_events(db_session)
    assert result == []


def test_get_all_events_returns_all_events(db_session):
    event_1 = Event(
        start_date=datetime.strptime("2023-01-01 10:00:00", "%Y-%m-%d %H:%M:%S"),
        end_date=datetime.strptime("2023-01-01 12:00:00", "%Y-%m-%d %H:%M:%S"),
        location="New York",
        attendees=50,
        note="Annual meeting",
    )
    event_2 = Event(
        start_date=datetime.strptime("2023-02-01 15:00:00", "%Y-%m-%d %H:%M:%S"),
        end_date=datetime.strptime("2023-02-01 17:00:00", "%Y-%m-%d %H:%M:%S"),
        location="San Francisco",
        attendees=30,
        note="Team meeting",
    )
    db_session.add(event_1)
    db_session.add(event_2)
    db_session.commit()

    result = get_all_events(db_session)
    assert len(result) == 2
    assert result[0].note == "Annual meeting"
    assert result[1].note == "Team meeting"


def test_get_all_events_with_partial_data(db_session):
    event = Event(
        start_date=datetime.strptime("2023-03-01 10:00:00", "%Y-%m-%d %H:%M:%S"),
        end_date=datetime.strptime("2023-03-01 12:00:00", "%Y-%m-%d %H:%M:%S"),
        location=None,
        attendees=None,
        note=None,
    )
    db_session.add(event)
    db_session.commit()

    result = get_all_events(db_session)
    assert len(result) == 1
    assert result[0].location is None
    assert result[0].attendees is None
    assert result[0].note is None
