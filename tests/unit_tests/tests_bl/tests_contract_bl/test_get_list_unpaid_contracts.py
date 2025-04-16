from unittest.mock import MagicMock

import pytest
from bl.contract_bl import ContractBL
from dal.contract_dal import ContractDAL
from dtos.contract_dto import ContractDTO
from security.permissions import is_commercial
from sqlalchemy.orm import Session


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def contract_dal(db_session):
    return MagicMock(spec=ContractDAL, db=db_session)


@pytest.fixture
def contract_bl(contract_dal):
    bl = ContractBL(db=contract_dal.db)
    bl.dal = contract_dal
    return bl


@pytest.fixture
def commercial_user():
    return {"role": "commercial", "id": 1}


@pytest.fixture
def non_commercial_user():
    return {"role": "admin", "id": 2}


@pytest.fixture
def unpaid_contracts():
    return [
        ContractDTO(id=1, total_amount=100.0, amount_left=50.0, creation_date=None, status=True, client_id=1,
                    commercial_id=1),
        ContractDTO(id=2, total_amount=200.0, amount_left=200.0, creation_date=None, status=True, client_id=2,
                    commercial_id=1)
    ]


@pytest.fixture
def paid_contracts():
    return [
        ContractDTO(id=3, total_amount=150.0, amount_left=0.0, creation_date=None, status=True, client_id=3,
                    commercial_id=1)
    ]


def test_list_unpaid_contract_as_commercial(contract_bl, contract_dal, commercial_user, unpaid_contracts,
                                            paid_contracts):
    contract_dal.get_all.return_value = unpaid_contracts + paid_contracts
    result = contract_bl.list_unpaid_contract(commercial_user)
    assert all(contract.amount_left > 0 for contract in result)
    assert result == unpaid_contracts


def test_list_unpaid_contract_as_non_commercial(contract_bl, non_commercial_user):
    with pytest.raises(PermissionError):
        contract_bl.list_unpaid_contract(non_commercial_user)


def test_list_unpaid_contract_with_no_unpaid(contract_bl, contract_dal, commercial_user, paid_contracts):
    contract_dal.get_all.return_value = paid_contracts
    result = contract_bl.list_unpaid_contract(commercial_user)
    assert result == []
