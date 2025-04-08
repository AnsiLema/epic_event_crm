from datetime import date

import pytest
from dtos.contract_dto import ContractDTO


def test_contract_dto_creation():
    dto = ContractDTO(
        id=1,
        total_amount=1000.0,
        amount_left=500.0,
        creation_date=date(2023, 10, 1),
        status=True,
        client_id=10,
        commercial_id=20
    )
    assert dto.id == 1
    assert dto.total_amount == 1000.0
    assert dto.amount_left == 500.0
    assert dto.creation_date == date(2023, 10, 1)
    assert dto.status is True
    assert dto.client_id == 10
    assert dto.commercial_id == 20


def test_contract_dto_negative_amounts():
    with pytest.raises(ValueError):
        ContractDTO(
            id=2,
            total_amount=-200.0,
            amount_left=-100.0,
            creation_date=date(2023, 10, 2),
            status=False,
            client_id=11,
            commercial_id=21
        )


def test_contract_dto_invalid_date():
    with pytest.raises(TypeError):
        ContractDTO(
            id=3,
            total_amount=1500.0,
            amount_left=750.0,
            creation_date="2023-10-01",
            status=False,
            client_id=12,
            commercial_id=22
        )


def test_contract_dto_boolean_status():
    with pytest.raises(TypeError):
        ContractDTO(
            id=4,
            total_amount=2000.0,
            amount_left=1000.0,
            creation_date=date(2023, 10, 3),
            status="active",
            client_id=13,
            commercial_id=23
        )