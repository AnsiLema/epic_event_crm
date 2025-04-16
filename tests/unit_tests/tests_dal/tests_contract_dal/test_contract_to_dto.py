from unittest.mock import MagicMock

import pytest
from dal.contract_dal import ContractDAL
from dtos.contract_dto import ContractDTO
from models.contract import Contract


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def contract_dal(mock_session):
    return ContractDAL(mock_session)


@pytest.fixture
def mock_contract():
    return Contract(
        id=1,
        total_amount=1000.50,
        amount_left=500.25,
        creation_date="2023-10-01",
        status=True,
        client_id=10,
        commercial_id=20
    )


def test_to_dto_conversion(contract_dal, mock_contract):
    result = contract_dal._to_dto(mock_contract)
    assert isinstance(result, ContractDTO)
    assert result.id == mock_contract.id
    assert result.total_amount == mock_contract.total_amount
    assert result.amount_left == mock_contract.amount_left
    assert result.creation_date == mock_contract.creation_date
    assert result.status == mock_contract.status
    assert result.client_id == mock_contract.client_id
    assert result.commercial_id == mock_contract.commercial_id
