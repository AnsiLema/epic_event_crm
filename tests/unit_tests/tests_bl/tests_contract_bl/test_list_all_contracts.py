from unittest.mock import MagicMock

import pytest
from bl.contract_bl import ContractBL
from dal.contract_dal import ContractDAL
from dtos.contract_dto import ContractDTO
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    """Fixture to provide a mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_contract_dal(mock_session):
    """Fixture to provide a mock ContractDAL instance."""
    return MagicMock(spec=ContractDAL, db=mock_session)


@pytest.fixture
def contract_bl(mock_contract_dal):
    """Fixture to provide a ContractBL instance with a mocked DAL."""
    bl = ContractBL(mock_contract_dal.db)
    bl.dal = mock_contract_dal
    return bl


def test_list_all_contracts_no_contracts(contract_bl):
    """Test the `list_all_contracts` method when no contracts are present."""
    contract_bl.dal.get_all.return_value = []
    result = contract_bl.list_all_contracts()
    assert result == []
    contract_bl.dal.get_all.assert_called_once()


def test_list_all_contracts_with_contracts(contract_bl):
    """Test the `list_all_contracts` method when contracts are present."""
    mock_contracts = [
        ContractDTO(
            id=1, total_amount=1000.0, amount_left=500.0,
            creation_date="2023-11-05", status=True,
            client_id=1, commercial_id=1
        ),
        ContractDTO(
            id=2, total_amount=2000.0, amount_left=0.0,
            creation_date="2023-10-15", status=False,
            client_id=2, commercial_id=2
        ),
    ]
    contract_bl.dal.get_all.return_value = mock_contracts
    result = contract_bl.list_all_contracts()
    assert result == mock_contracts
    contract_bl.dal.get_all.assert_called_once()
