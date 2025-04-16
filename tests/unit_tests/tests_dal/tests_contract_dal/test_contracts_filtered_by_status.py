from unittest.mock import MagicMock

import pytest
from dal.contract_dal import ContractDAL
from dtos.contract_dto import ContractDTO
from models.contract import Contract


def test_filter_by_status_signed(mocker):
    mock_db = MagicMock()
    contracts = [
        Contract(id=1, total_amount=1000.00, amount_left=500.00, creation_date="2023-01-01", status=True, client_id=1,
                 commercial_id=2),
        Contract(id=2, total_amount=2000.00, amount_left=1000.00, creation_date="2023-06-01", status=True, client_id=3,
                 commercial_id=4),
    ]
    mock_db.query().filter_by().all.return_value = contracts

    contract_dal = ContractDAL(mock_db)
    mocker.patch.object(ContractDAL, "_to_dto", side_effect=lambda c: ContractDTO(
        id=c.id,
        total_amount=c.total_amount,
        amount_left=c.amount_left,
        creation_date=c.creation_date,
        status=c.status,
        client_id=c.client_id,
        commercial_id=c.commercial_id,
    ))

    result = contract_dal.filter_by_status(signed=True)

    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2
    mock_db.query().filter_by.assert_called_with(status=True)


def test_filter_by_status_unsigned(mocker):
    mock_db = MagicMock()
    contracts = [
        Contract(id=3, total_amount=1500.00, amount_left=250.00, creation_date="2023-02-01", status=False, client_id=5,
                 commercial_id=6),
    ]
    mock_db.query().filter_by().all.return_value = contracts

    contract_dal = ContractDAL(mock_db)
    mocker.patch.object(ContractDAL, "_to_dto", side_effect=lambda c: ContractDTO(
        id=c.id,
        total_amount=c.total_amount,
        amount_left=c.amount_left,
        creation_date=c.creation_date,
        status=c.status,
        client_id=c.client_id,
        commercial_id=c.commercial_id,
    ))

    result = contract_dal.filter_by_status(signed=False)

    assert len(result) == 1
    assert result[0].id == 3
    mock_db.query().filter_by.assert_called_with(status=False)


def test_filter_by_status_no_results(mocker):
    mock_db = MagicMock()
    mock_db.query().filter_by().all.return_value = []

    contract_dal = ContractDAL(mock_db)

    result = contract_dal.filter_by_status(signed=True)

    assert len(result) == 0
    mock_db.query().filter_by.assert_called_with(status=True)
