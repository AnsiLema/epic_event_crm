from unittest.mock import MagicMock

import pytest
from dal.client_dal import ClientDAL
from dtos.client_dto import ClientDTO
from models.client import Client
from sqlalchemy.orm import Session


@pytest.fixture
def db_session():
    """Fixture for a mocked database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def client_dal(db_session):
    """Fixture for a ClientDAL instance."""
    return ClientDAL(db=db_session)


@pytest.fixture
def client_instance():
    """Fixture for a mocked Client instance."""
    return Client(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        phone="1234567890",
        company="Test Company",
        creation_date="2023-01-01",
        last_contact_date="2023-10-01",
        commercial_id=2,
    )


def test_update_by_id_successful(db_session, client_dal, client_instance):
    """Test `update_by_id` updates a client successfully."""
    db_session.query.return_value.filter_by.return_value.first.return_value = client_instance
    updates = {"name": "Jane Doe", "email": "jane.doe@example.com"}

    result = client_dal.update_by_id(client_id=1, updates=updates)

    db_session.query.assert_called_once()
    db_session.query.return_value.filter_by.assert_called_once_with(id=1)
    assert isinstance(result, ClientDTO)
    assert result.name == "Jane Doe"
    assert result.email == "jane.doe@example.com"


def test_update_by_id_client_not_found(db_session, client_dal):
    """Test `update_by_id` when client is not found."""
    db_session.query.return_value.filter_by.return_value.first.return_value = None
    updates = {"name": "Jane Doe", "email": "jane.doe@example.com"}

    result = client_dal.update_by_id(client_id=1, updates=updates)

    db_session.query.assert_called_once()
    db_session.query.return_value.filter_by.assert_called_once_with(id=1)
    assert result is None
