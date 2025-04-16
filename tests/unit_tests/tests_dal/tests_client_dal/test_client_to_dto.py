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
        company="Acme Corp",
        creation_date=date(2022, 1, 1),
        last_contact_date=date(2023, 1, 1),
        commercial_id=42
    )


@pytest.fixture
def client_dal():
    db_session = MagicMock(spec=Session)
    return ClientDAL(db=db_session)


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


def test_to_dto_with_no_optional_fields(client_dal):
    """Test `_to_dto` when optional fields are not set in the `Client` instance."""
    client_instance = Client(
        id=2,
        name="Jane Smith",
        email="jane.smith@example.com",
        phone=None,
        company=None,
        creation_date=date(2022, 6, 15),
        last_contact_date=None,
        commercial_id=99
    )
    dto = client_dal._to_dto(client_instance)
    assert isinstance(dto, ClientDTO)
    assert dto.id == client_instance.id
    assert dto.name == client_instance.name
    assert dto.email == client_instance.email
    assert dto.phone is None
    assert dto.company is None
    assert dto.creation_date == client_instance.creation_date
    assert dto.last_contact_date is None
    assert dto.commercial_id == client_instance.commercial_id
