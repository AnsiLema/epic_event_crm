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
def test_create_contract_success(mock_perm, contract_bl):
    # Arrange
    current_user = {"role": "commercial", "sub": "user@example.com"}
    contract_data = {
        "client_id": 1,
        "total_amount": 1000,
        "amount_left": 200,
        "creation_date": "2025-01-01",
        "commercial_id": 1,
        "status": False
    }
    expected_result = ContractDTO(
        id=1,
        client_id=1,
        total_amount=1000,
        amount_left=200,
        creation_date="2025-01-01",
        commercial_id=1,
        status=False
    )
    contract_bl.dal.create.return_value = expected_result

    # Act
    result = contract_bl.create_contract(contract_data, current_user)

    # Assert
    assert isinstance(result, ContractDTO)
    assert result.client_id == 1
    assert result.total_amount == 1000
    assert result.status == False


@patch("bl.contract_bl.can_manage_contracts", return_value=False)
def test_create_contract_permission_denied(mock_perm, contract_bl):
    current_user = {"role": "support", "sub": "unauthorized@example.com"}
    with pytest.raises(PermissionError, match="Vous n'avez pas les droits pour créer un contrat."):
        contract_bl.create_contract({"client_id": 1, "amount": 1000, "status": "draft"}, current_user)