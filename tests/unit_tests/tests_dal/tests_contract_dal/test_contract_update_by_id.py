from unittest.mock import MagicMock

import pytest
from dal.contract_dal import ContractDAL
from dtos.contract_dto import ContractDTO
from models.contract import Contract
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def contract_dal(mock_session):
    return ContractDAL(mock_session)


@pytest.fixture
def mock_contract():
    return Contract(
        id=1,
        total_amount=1000.0,
        amount_left=500.0,
        creation_date="2023-10-01",
        status=True,
        client_id=123,
        commercial_id=456
    )


def test_update_by_id_existing_contract(contract_dal, mock_session, mock_contract):
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_contract
    mock_session.query.return_value.filter_by.return_value.update.return_value = 1

    result = contract_dal.update_by_id(1, {"status": False})

    assert result is not None
    assert result.id == mock_contract.id
    assert result.status is False


def test_update_by_id_non_existing_contract(contract_dal, mock_session):
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    result = contract_dal.update_by_id(2, {"status": True})

    assert result is None


def test_update_by_id_invalid_updates(contract_dal, mock_session, mock_contract):
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_contract

    with pytest.raises(Exception):
        contract_dal.update_by_id(1, None)
