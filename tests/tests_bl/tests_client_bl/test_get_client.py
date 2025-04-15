from unittest.mock import MagicMock, patch

import pytest
from bl.client_bl import ClientBLL
from dal.client_dal import ClientDAL
from dtos.client_dto import ClientDTO
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_client_dal(mock_session):
    return MagicMock(spec=ClientDAL, db=mock_session)


@pytest.fixture
def client_bll(mock_session, mock_client_dal):
    with patch("bl.client_bl.ClientDAL", return_value=mock_client_dal):
        yield ClientBLL(db=mock_session)


@pytest.fixture
def valid_client_dto():
    return ClientDTO(
        id=1,
        name="Test Client",
        email="test@test.com",
        phone="1234567890",
        company="Test Company",
        creation_date="2023-01-01",
        last_contact_date=None,
        commercial_id=5,
    )


def test_get_client_success(client_bll, mock_client_dal, valid_client_dto):
    mock_client_dal.get.return_value = valid_client_dto
    result = client_bll.get_client(1)
    assert result == valid_client_dto
    mock_client_dal.get.assert_called_once_with(1)


def test_get_client_not_found(client_bll, mock_client_dal):
    mock_client_dal.get.return_value = None
    with pytest.raises(ValueError, match="client introuvable"):
        client_bll.get_client(999)
    mock_client_dal.get.assert_called_once_with(999)
