# File: tests/test_client_dal.py

from datetime import date
from unittest.mock import MagicMock

import pytest
from dal.client_dal import ClientDAL
from dtos.client_dto import ClientDTO
from models.client import Client
from sqlalchemy.orm import Session


@pytest.fixture
def client_instance():
    return Client(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        phone="123-456-7890",
        company="Example Co.",
        creation_date=date(2023, 1, 1),
        last_contact_date=date(2023, 9, 1),
        commercial_id=101
    )


@pytest.fixture
def session_mock():
    """Fixture to mock the SQLAlchemy session."""
    return MagicMock(spec=Session)


@pytest.fixture
def client_dal(session_mock):
    """Fixture to initialize the ClientDAL instance."""
    return ClientDAL(db=session_mock)


def test_to_dto_conversion(client_instance, client_dal):
    """Test the `_to_dto` method for proper conversion."""
    dto = client_dal._to_dto(client_instance)
    assert isinstance(dto, ClientDTO)
    assert dto.id == client_instance.id
    assert dto.name == client_instance.name
    assert dto.email == client_instance.email
    assert dto.phone == client_instance.phone
    assert dto.company == client_instance.company
    assert dto.creation_date == client_instance.creation_date
    assert dto.last_contact_date == client_instance.last_contact_date
    assert dto.commercial_id == client_instance.commercial_id


def test_get_client_found(client_dal, session_mock, client_instance, mocker):
    """Test the `get` method for a case where the client is found."""
    # Arrange
    client_id = client_instance.id
    session_mock.query.return_value.filter_by.return_value.first.return_value = client_instance

    expected_dto = ClientDTO(
        id=client_instance.id,
        name=client_instance.name,
        email=client_instance.email,
        phone=client_instance.phone,
        company=client_instance.company,
        creation_date=client_instance.creation_date,
        last_contact_date=client_instance.last_contact_date,
        commercial_id=client_instance.commercial_id
    )

    mocker.patch.object(client_dal, '_to_dto', return_value=expected_dto)

    # Act
    result = client_dal.get(client_id)

    # Assert
    assert result == expected_dto


def test_get_client_not_found(client_dal, session_mock):
    """Test the `get` method for a case where the client is not found."""
    # Arrange
    client_id = 999
    session_mock.query.return_value.filter_by.return_value.first.return_value = None

    # Act
    result = client_dal.get(client_id)

    # Assert
    assert result is None


def test_get_invalid_id(client_dal, session_mock):
    """Test the `get` method for a case with an invalid client ID."""
    # Arrange
    invalid_client_id = "invalid_id"

    # Act and Assert
    with pytest.raises(Exception):
        client_dal.get(invalid_client_id)


def test_to_dto_null_values(client_dal):
    """Test the `_to_dto` method with a client instance with null optional fields."""
    client_instance = Client(
        id=2,
        name="Jane Doe",
        email="jane.doe@example.com",
        phone=None,
        company=None,
        creation_date=date(2023, 3, 14),
        last_contact_date=None,
        commercial_id=102
    )

    dto = client_dal._to_dto(client_instance)
    assert isinstance(dto, ClientDTO)
    assert dto.id == client_instance.id
    assert dto.name == client_instance.name
    assert dto.email == client_instance.email
    assert dto.phone == client_instance.phone
    assert dto.company == client_instance.company
    assert dto.creation_date == client_instance.creation_date
    assert dto.last_contact_date == client_instance.last_contact_date
    assert dto.commercial_id == client_instance.commercial_id
