from unittest.mock import MagicMock

import pytest
from dal.contract_dal import ContractDAL
from dtos.contract_dto import ContractDTO
from models.contract import Contract


def test_get_all_with_no_records(mocker):
    mock_db_session = MagicMock()
    mock_db_session.query.return_value.all.return_value = []
    contract_dal = ContractDAL(mock_db_session)

    result = contract_dal.get_all()

    assert result == []


def test_get_all_with_existing_records(mocker):
    mock_db_session = MagicMock()
    mock_contracts = [
        Contract(id=1, total_amount=1000.0, amount_left=500.0, creation_date="2023-01-01", status=True, client_id=1,
                 commercial_id=1),
        Contract(id=2, total_amount=2000.0, amount_left=1500.0, creation_date="2023-01-02", status=False, client_id=2,
                 commercial_id=2)
    ]
    mock_dto_list = [
        ContractDTO(id=1, total_amount=1000.0, amount_left=500.0, creation_date="2023-01-01", status=True, client_id=1,
                    commercial_id=1),
        ContractDTO(id=2, total_amount=2000.0, amount_left=1500.0, creation_date="2023-01-02", status=False,
                    client_id=2, commercial_id=2)
    ]
    mock_db_session.query.return_value.all.return_value = mock_contracts
    contract_dal = ContractDAL(mock_db_session)

    mocker.patch.object(contract_dal, "_to_dto",
                        side_effect=lambda c: next(dto for dto in mock_dto_list if dto.id == c.id))
    result = contract_dal.get_all()

    assert len(result) == len(mock_dto_list)
    assert isinstance(result[0], ContractDTO)
    assert result[0].id == mock_contracts[0].id
    assert result[1].id == mock_contracts[1].id
