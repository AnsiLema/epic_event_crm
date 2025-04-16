from unittest.mock import MagicMock, patch

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
    return ContractDAL(db_session)


@pytest.fixture
def contract_bl(contract_dal):
    bl = ContractBL(MagicMock(spec=Session))
    bl.dal = contract_dal
    return bl


@pytest.fixture
def sample_contracts():
    return [
        ContractDTO(id=1, total_amount=1000, amount_left=500, creation_date="2023-01-01", status=True, client_id=1,
                    commercial_id=1),
        ContractDTO(id=2, total_amount=1500, amount_left=0, creation_date="2023-02-01", status=True, client_id=2,
                    commercial_id=2),
    ]


@pytest.fixture
def current_user_commercial():
    return {"id": 1, "role": "commercial"}


@pytest.fixture
def current_user_non_commercial():
    return {"id": 2, "role": "admin"}


def test_list_signed_contracts_as_commercial(contract_bl, sample_contracts, current_user_commercial):
    """Test that `list_signed_contracts` returns correct data for commercial users."""
    contract_bl.dal.filter_by_status = MagicMock(return_value=sample_contracts)
    result = contract_bl.list_signed_contracts(current_user_commercial)
    assert result == sample_contracts
    contract_bl.dal.filter_by_status.assert_called_once_with(signed=True)


def test_list_signed_contracts_as_non_commercial(contract_bl, current_user_non_commercial):
    """Test that `list_signed_contracts` raises PermissionError for non-commercial users."""
    with pytest.raises(PermissionError, match="Seuls les commerciaux peuvent filtrer les contrats."):
        contract_bl.list_signed_contracts(current_user_non_commercial)


def test_list_signed_contracts_permission_check(contract_bl, current_user_commercial):
    """Test that `is_commercial` is called to check permissions."""
    with patch("bl.contract_bl.is_commercial", MagicMock(return_value=True)) as mock_is_commercial:
        contract_bl.dal.filter_by_status = MagicMock(return_value=[])
        contract_bl.list_signed_contracts(current_user_commercial)
        mock_is_commercial.assert_called_once_with(current_user_commercial)
