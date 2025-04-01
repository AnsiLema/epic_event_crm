from unittest.mock import MagicMock

import pytest
from models.client import Client
from models.collaborator import Collaborator
from services.client_service import create_client
from sqlalchemy.orm import Session


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def commercial_user():
    return Collaborator(id=1, name="Test User", email="commercial@example.com")


@pytest.fixture
def non_commercial_payload():
    return {"role": "non-commercial", "sub": "non_commercial_user@example.com"}


@pytest.fixture
def commercial_payload():
    return {"role": "commercial", "sub": "commercial@example.com"}


def test_create_client_non_commercial_role(db_session, non_commercial_payload):
    result = create_client(
        db=db_session,
        payload=non_commercial_payload,
        name="Test Client",
        email="client@example.com",
        phone="1234567890",
        company="Test Company"
    )
    assert result is None


def test_create_client_commercial_not_found(db_session, commercial_payload):
    db_session.query().filter_by().first.return_value = None
    result = create_client(
        db=db_session,
        payload=commercial_payload,
        name="Test Client",
        email="client@example.com",
        phone="1234567890",
        company="Test Company"
    )
    assert result is None


def test_create_client_success(db_session, commercial_payload, commercial_user):
    db_session.query().filter_by().first.return_value = commercial_user

    new_client = Client(
        name="Test Client",
        email="client@example.com",
        phone="1234567890",
        company="Test Company",
        commercial_id=commercial_user.id
    )

    result = create_client(
        db=db_session,
        payload=commercial_payload,
        name=new_client.name,
        email=new_client.email,
        phone=new_client.phone,
        company=new_client.company
    )

    assert result is not None
    assert isinstance(result, Client)
    assert result.name == new_client.name
    assert result.email == new_client.email
    assert result.phone == new_client.phone
    assert result.company == new_client.company
    assert result.commercial_id == commercial_user.id
