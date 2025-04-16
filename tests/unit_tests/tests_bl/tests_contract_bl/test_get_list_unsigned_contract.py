from unittest.mock import patch, MagicMock

import pytest
from bl.contract_bl import ContractBL
from dtos.contract_dto import ContractDTO


@patch("bl.contract_bl.is_commercial", return_value=True)
def test_list_unsigned_contracts_as_commercial(mock_is_commercial):
    # Arrange
    current_user = {"role": "commercial"}
    unsigned_contracts = [
        ContractDTO(
            id=1,
            total_amount=1000,
            amount_left=1000,
            creation_date="2025-01-01",
            status=False,
            client_id=1,
            commercial_id=2,
        ),
        ContractDTO(
            id=2,
            total_amount=2000,
            amount_left=500,
            creation_date="2025-01-05",
            status=False,
            client_id=3,
            commercial_id=4,
        ),
    ]
    contract_bl = ContractBL(db=None)
    contract_bl.dal = MagicMock()
    contract_bl.dal.filter_by_status.return_value = unsigned_contracts

    # Act
    result = contract_bl.list_unsigned_contracts(current_user)

    # Assert
    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2
    assert result[0].status is False
    assert result[1].status is False


@patch("bl.contract_bl.is_commercial", return_value=False)
def test_list_unsigned_contracts_without_permission(mock_is_commercial):
    # Arrange
    current_user = {"role": "client"}
    contract_bl = ContractBL(db=None)

    # Act & Assert
    with pytest.raises(PermissionError) as exc_info:
        contract_bl.list_unsigned_contracts(current_user)
    assert str(exc_info.value) == "Seuls les commerciaux peuvent filtrer les contrats."
