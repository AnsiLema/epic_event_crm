from unittest.mock import MagicMock

import pytest
from dal.contract_dal import ContractDAL
from dtos.contract_dto import ContractDTO
from models.contract import Contract
from sqlalchemy.orm import Session


def test_update_existing_contract(mocker):
    db_session = MagicMock(spec=Session)
    mock_contract = Contract(
        id=1,
        total_amount=500.0,
        amount_left=200.0,
        creation_date="2023-01-01",
        status=False,
        client_id=1,
        commercial_id=1,
    )

    # On configure l’enchaînement query().filter_by().first()
    mock_query = db_session.query.return_value
    mock_filter = mock_query.filter_by.return_value
    mock_filter.first.return_value = mock_contract

    db_session.commit = MagicMock()
    db_session.refresh = MagicMock()

    dal = ContractDAL(db=db_session)
    updates = {"status": True}
    updated_contract = dal.update(contract_id=1, updates=updates)

    assert updated_contract.status is True
    mock_query.filter_by.assert_any_call(id=1)


def test_update_nonexistent_contract(mocker):
    db_session = MagicMock(spec=Session)

    # Chaîne d’appel
    mock_query = db_session.query.return_value
    mock_filter = mock_query.filter_by.return_value
    mock_filter.first.return_value = None  # Aucun contrat trouvé

    dal = ContractDAL(db=db_session)

    updates = {"status": True}
    updated_contract = dal.update(contract_id=999, updates=updates)

    assert updated_contract is None
    mock_query.filter_by.assert_any_call(id=999)
