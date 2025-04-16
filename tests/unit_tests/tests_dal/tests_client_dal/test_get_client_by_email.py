from unittest.mock import MagicMock

import pytest
from dal.client_dal import ClientDAL
from dtos.client_dto import ClientDTO
from models.client import Client
from sqlalchemy.orm import Session


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def client_dal(db_session):
    return ClientDAL(db_session)


@pytest.fixture
def client_instance():
    return Client(
        id=1,
        name="John Doe",
        email="johndoe@example.com",
        phone="1234567890",
        company="ExampleCorp",
        creation_date="2023-01-01",
        last_contact_date="2023-06-01",
        commercial_id=2
    )


def test_get_by_email_existing(client_instance, db_session, client_dal):
    """Test `get_by_email` when the client exists."""
    db_session.query.return_value.filter_by.return_value.first.return_value = client_instance

    result = client_dal.get_by_email("johndoe@example.com")

    assert isinstance(result, ClientDTO)
    assert result.id == client_instance.id
    assert result.name == client_instance.name
    assert result.email == client_instance.email


def test_get_by_email_nonexistent(db_session, client_dal):
    """Test `get_by_email` when the client does not exist."""
    db_session.query.return_value.filter_by.return_value.first.return_value = None

    result = client_dal.get_by_email("notfound@example.com")

    assert result is None
