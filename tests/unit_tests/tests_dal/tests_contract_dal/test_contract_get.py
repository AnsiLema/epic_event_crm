from unittest.mock import Mock

import pytest
from dal.contract_dal import ContractDAL
from dtos.contract_dto import ContractDTO
from models.contract import Contract
from sqlalchemy.orm import Session


def test_get_returns_contract_dto(mocker):
    # Arrange
    mock_session = Mock(spec=Session)
    mock_contract = Mock(spec=Contract)
    mock_contract.id = 1
    mock_contract.total_amount = 1000.00
    mock_contract.amount_left = 500.00
    mock_contract.creation_date = "2023-10-01"
    mock_contract.status = True
    mock_contract.client_id = 1
    mock_contract.commercial_id = 2

    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_contract
    dal = ContractDAL(db=mock_session)
    mocker.patch.object(dal, "_to_dto", return_value=ContractDTO(
        id=mock_contract.id,
        total_amount=float(mock_contract.total_amount),
        amount_left=float(mock_contract.amount_left),
        creation_date=mock_contract.creation_date,
        status=mock_contract.status,
        client_id=mock_contract.client_id,
        commercial_id=mock_contract.commercial_id,
    ))

    # Act
    result = dal.get(contract_id=1)

    # Assert
    assert isinstance(result, ContractDTO)
    assert result.id == 1
    assert result.total_amount == 1000.00
    assert result.amount_left == 500.00
    assert result.creation_date == "2023-10-01"
    assert result.status is True
    assert result.client_id == 1
    assert result.commercial_id == 2


def test_get_returns_none_if_not_found():
    # Arrange
    mock_session = Mock(spec=Session)
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    dal = ContractDAL(db=mock_session)

    # Act
    result = dal.get(contract_id=1)

    # Assert
    assert result is None
