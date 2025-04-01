import pytest
from unittest.mock import MagicMock
from models.client import Client
from models.collaborator import Collaborator
from services.client_service import update_client


@pytest.fixture
def db_session():
    return MagicMock()

@pytest.fixture
def commercial_user():
    return Collaborator(id=1, email="commercial@example.com")

@pytest.fixture
def commercial_payload():
    return {"role": "commercial", "sub": "commercial@example.com"}

def test_update_client_success(db_session, commercial_payload, commercial_user):
    client = Client(id=10, name="Old", email="old@mail.com",
                    phone="000", company="OldCo", commercial_id=commercial_user.id)

    db_session.query().filter_by().first.side_effect = [
        commercial_user,  # current_user
        client            # client
    ]

    updated = update_client(
        db=db_session,
        payload=commercial_payload,
        client_id=10,
        name="New Name",
        phone="0600000000"
    )

    assert updated is not None
    assert updated.name == "New Name"
    assert updated.phone == "0600000000"

def test_update_client_user_not_found(db_session):
    db_session.query().filter_by().first.return_value = None

    payload = {"role": "commercial", "sub": "unknown@mail.com"}

    result = update_client(db_session, payload, client_id=1, name="Test")
    assert result is None

def test_update_client_not_responsible(db_session, commercial_payload):
    other_commercial = Collaborator(id=2, email="other@mail.com")
    client = Client(id=1, name="Client", commercial_id=999)  # not assigned to user

    db_session.query().filter_by().first.side_effect = [
        other_commercial,  # current_user
        client
    ]

    result = update_client(db_session, commercial_payload, client_id=1, name="Blocked")
    assert result is None

def test_update_client_with_non_commercial_role(db_session):
    client = Client(id=1, name="Client", commercial_id=1)

    db_session.query().filter_by().first.side_effect = [
        Collaborator(id=1, email="gestion@example.com"),
        client
    ]

    payload = {"role": "gestion", "sub": "gestion@example.com"}

    result = update_client(db_session, payload, client_id=1, name="Nope")
    assert result is None

def test_update_client_not_found(db_session, commercial_payload, commercial_user):
    db_session.query().filter_by().first.side_effect = [
        commercial_user,
        None  # client not found
    ]

    result = update_client(db_session, commercial_payload, client_id=99, name="Does not exist")
    assert result is None
