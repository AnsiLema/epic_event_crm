from datetime import date
from unittest.mock import MagicMock

import pytest
from dal.client_dal import ClientDAL
from dtos.client_dto import ClientDTO
from models.client import Client
from sqlalchemy.orm import Session


@pytest.fixture
def db_session():
    """Fixture to mock the database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def client_dal(db_session):
    """Fixture to initialize the ClientDAL instance."""
    return ClientDAL(db=db_session)


@pytest.fixture
def client_data():
    """Fixture to provide sample client data."""
    return {
        "id": 1,
        "name": "John Doe",
        "email": "johndoe@example.com",
        "phone": "123456789",
        "company": "Example Corp",
        "creation_date": date(2023, 1, 1),
        "last_contact_date": date(2023, 10, 1),
        "commercial_id": 42,
    }


@pytest.fixture
def client_instance(client_data):
    """Fixture to provide a mocked Client instance."""
    client = MagicMock(spec=Client)
    for key, value in client_data.items():
        setattr(client, key, value)
    return client


@pytest.fixture
def client_dto(client_data):
    """Fixture to provide a ClientDTO instance."""
    return ClientDTO(**client_data)


def test_create(client_dal, db_session, client_data, client_dto):
    """Test the `create` method of ClientDAL."""
    client_dal._to_dto = MagicMock(return_value=client_dto)

    result = client_dal.create(data=client_data)

    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()

    refreshed_obj = db_session.refresh.call_args.args[0]
    assert isinstance(refreshed_obj, Client)
    assert refreshed_obj.email == client_data["email"]

    assert result == client_dto


def test_create_with_invalid_data(client_dal, db_session):
    """Test the `create` method with invalid data."""
    with pytest.raises(TypeError):
        client_dal.create(data=None)
