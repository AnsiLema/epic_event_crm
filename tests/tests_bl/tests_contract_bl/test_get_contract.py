from unittest.mock import patch, MagicMock

import pytest
from bl.contract_bl import ContractBL
from dtos.contract_dto import ContractDTO


@patch("bl.contract_bl.ContractDAL")
def test_get_contract_success(mock_dal):
    # Arrange
    contract_id = 1
    expected_contract = ContractDTO(
        id=1,
        total_amount=1000.0,
        amount_left=200.0,
        creation_date="2025-01-01",
        status=True,
        client_id=2,
        commercial_id=3
    )
    mock_dal_instance = mock_dal.return_value
    mock_dal_instance.get.return_value = expected_contract
    contract_bl = ContractBL(db=MagicMock())
    contract_bl.dal = mock_dal_instance

    # Act
    result = contract_bl.get_contract(contract_id)

    # Assert
    assert isinstance(result, ContractDTO)
    assert result.id == expected_contract.id
    assert result.total_amount == expected_contract.total_amount
    assert result.creation_date == expected_contract.creation_date


@patch("bl.contract_bl.ContractDAL")
def test_get_contract_not_found(mock_dal):
    # Arrange
    contract_id = 999
    mock_dal_instance = mock_dal.return_value
    mock_dal_instance.get.return_value = None
    contract_bl = ContractBL(db=MagicMock())
    contract_bl.dal = mock_dal_instance

    # Act & Assert
    with pytest.raises(ValueError, match="Contrat introuvable."):
        contract_bl.get_contract(contract_id)
