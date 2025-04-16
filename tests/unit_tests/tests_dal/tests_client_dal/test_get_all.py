from unittest.mock import MagicMock

import pytest
from dal.client_dal import ClientDAL
from dtos.client_dto import ClientDTO
from models.client import Client
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def client_dal(mock_session):
    return ClientDAL(db=mock_session)


@pytest.fixture
def mock_clients():
    return [
        Client(
            id=1,
            name="John Doe",
            email="john.doe@example.com",
            phone="123456789",
            company="Example Corp",
            creation_date="2023-01-01",
            last_contact_date="2023-05-10",
            commercial_id=99,
        ),
        Client(
            id=2,
            name="Jane Smith",
            email="jane.smith@example.com",
            phone="987654321",
            company=None,
            creation_date="2023-06-01",
            last_contact_date=None,
            commercial_id=100,
        ),
    ]


def test_get_all_clients(mock_session, client_dal, mock_clients):
    """Test that `get_all` retrieves all clients and converts them to DTOs."""
    mock_session.query.return_value.all.return_value = mock_clients
    client_dal._to_dto = MagicMock(
        side_effect=lambda client: ClientDTO(
            id=client.id,
            name=client.name,
            email=client.email,
            phone=client.phone,
            company=client.company,
            creation_date=client.creation_date,
            last_contact_date=client.last_contact_date,
            commercial_id=client.commercial_id,
        )
    )

    result = client_dal.get_all()

    assert len(result) == len(mock_clients)
    for mock_client, dto in zip(mock_clients, result):
        assert isinstance(dto, ClientDTO)
        assert dto.id == mock_client.id
        assert dto.name == mock_client.name
        assert dto.email == mock_client.email
        assert dto.phone == mock_client.phone
        assert dto.company == mock_client.company
        assert dto.creation_date == mock_client.creation_date
        assert dto.last_contact_date == mock_client.last_contact_date
        assert dto.commercial_id == mock_client.commercial_id


def test_get_all_no_clients(mock_session, client_dal):
    """Test that `get_all` returns an empty list when there are no clients."""
    mock_session.query.return_value.all.return_value = []
    client_dal._to_dto = MagicMock()

    result = client_dal.get_all()

    assert result == []
    client_dal._to_dto.assert_not_called()
