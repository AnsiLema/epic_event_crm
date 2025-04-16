import pytest
from unittest.mock import patch, MagicMock
from bl.contract_bl import ContractBL
from dtos.contract_dto import ContractDTO


@pytest.fixture
def contract_bl():
    fake_db = MagicMock()
    bl = ContractBL(fake_db)
    bl.dal = MagicMock()
    return bl


@patch("bl.contract_bl.can_manage_contracts", return_value=True)
@patch("bl.contract_bl.is_commercial", return_value=False)
def test_update_contract_success_non_commercial(mock_is_commercial, mock_can_manage, contract_bl):
    current_user = {"id": 99, "role": "admin"}
    contract = MagicMock(commercial_id=88)
    contract_bl.dal.get.return_value = contract
    contract_bl.dal.update_by_id.return_value = ContractDTO(
        id=1, client_id=2, total_amount=1500, amount_left=200, status=True, creation_date="2025-01-01", commercial_id=88
    )

    updates = {"status": "signed", "total_amount": 1500}

    result = contract_bl.update_contract(1, updates, current_user)
    assert isinstance(result, ContractDTO)
    assert result.total_amount == 1500
    assert result.status == True


@patch("bl.contract_bl.can_manage_contracts", return_value=True)
@patch("bl.contract_bl.is_commercial", return_value=True)
def test_update_contract_success_commercial_owner(mock_is_commercial, mock_can_manage, contract_bl):
    current_user = {"id": 42, "role": "commercial"}
    contract = MagicMock(commercial_id=42)
    contract_bl.dal.get.return_value = contract
    contract_bl.dal.update_by_id.return_value = ContractDTO(
        id=2, client_id=3, total_amount=2000, amount_left=200, creation_date="2025-01-01", status=True, commercial_id=42
    )

    result = contract_bl.update_contract(2, {"amount": 2000}, current_user)
    assert isinstance(result, ContractDTO)
    assert result.total_amount == 2000


def test_update_contract_not_found(contract_bl):
    contract_bl.dal.get.return_value = None
    with pytest.raises(ValueError, match="Contrat introuvable."):
        contract_bl.update_contract(99, {}, {"id": 1, "role": "admin"})


@patch("bl.contract_bl.can_manage_contracts", return_value=False)
def test_update_contract_permission_denied_global(mock_can_manage, contract_bl):
    contract_bl.dal.get.return_value = MagicMock()
    with pytest.raises(PermissionError, match="Vous n'avez pas les droits pour modifier ce contrat."):
        contract_bl.update_contract(1, {}, {"id": 1, "role": "support"})


@patch("bl.contract_bl.can_manage_contracts", return_value=True)
@patch("bl.contract_bl.is_commercial", return_value=True)
def test_update_contract_permission_denied_commercial_other_contract(mock_is_commercial, mock_can_manage, contract_bl):
    current_user = {"id": 10, "role": "commercial"}
    contract = MagicMock(commercial_id=99)
    contract_bl.dal.get.return_value = contract

    with pytest.raises(PermissionError, match="Vous ne pouvez modifier que les contrats de vos clients."):
        contract_bl.update_contract(1, {"amount": 1000}, current_user)