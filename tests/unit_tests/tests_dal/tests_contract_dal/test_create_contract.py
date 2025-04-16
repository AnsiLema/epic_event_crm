import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from dal.contract_dal import ContractDAL
from dtos.contract_dto import ContractDTO
from models.contract import Contract


def test_create_contract_successful(mocker):
    # Arrange
    mock_session = MagicMock(spec=Session)
    sample_data = {
        "total_amount": 5000.0,
        "amount_left": 3000.0,
        "creation_date": "2023-11-01",
        "status": False,
        "client_id": 1,
        "commercial_id": 2
    }

    expected_dto = ContractDTO(
        id=1,
        total_amount=5000.0,
        amount_left=3000.0,
        creation_date="2023-11-01",
        status=False,
        client_id=1,
        commercial_id=2
    )

    # Mock session behavior
    mocker.patch.object(mock_session, "add")
    mocker.patch.object(mock_session, "commit")
    mocker.patch.object(mock_session, "refresh", side_effect=lambda obj: None)
    mock_to_dto = mocker.patch.object(ContractDAL, "_to_dto", return_value=expected_dto)

    contract_dal = ContractDAL(db=mock_session)

    # Act
    result = contract_dal.create(sample_data)

    # Assert
    assert mock_session.add.call_count == 1
    added_contract = mock_session.add.call_args.args[0]
    assert isinstance(added_contract, Contract)
    assert added_contract.total_amount == 5000.0
    assert added_contract.client_id == 1

    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(added_contract)
    mock_to_dto.assert_called_once_with(added_contract)

    assert isinstance(result, ContractDTO)
    assert result.total_amount == 5000.0


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def contract_dal(db_session):
    return ContractDAL(db_session)


def test_create_contract_missing_required_field_raises_integrity_error(contract_dal, db_session):
    # Arrange — missing "total_amount"
    incomplete_data = {
        "amount_left": 3000.0,
        "creation_date": "2023-11-01",
        "status": False,
        "client_id": 1,
        "commercial_id": 2
    }

    db_session.commit.side_effect = IntegrityError("INSERT", {}, Exception("NOT NULL violation"))

    contract_dal._to_dto = MagicMock()

    # Act & Assert
    with pytest.raises(IntegrityError):
        contract_dal.create(incomplete_data)

    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()


def test_create_contract_invalid_field(mocker):
    # Arrange
    mock_session = MagicMock(spec=Session)
    contract_dal = ContractDAL(db=mock_session)

    sample_data = {
        "total_amount": 5000.0,
        "amount_left": 3000.0,
        "creation_date": "2023-11-01",
        "status": False,
        "client_id": 1,
        "commercial_id": 2,
        "invalid_field": "unexpected"
    }

    # Act & Assert
    with pytest.raises(TypeError):
        contract_dal.create(sample_data)