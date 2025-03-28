import pytest
from security.permissions import can_manage_contracts


def test_can_manage_contracts_with_valid_permission():
    payload = {"role": "gestion"}
    assert can_manage_contracts(payload) is True


def test_can_manage_contracts_with_another_valid_permission():
    payload = {"role": "commercial"}
    assert can_manage_contracts(payload) is True


def test_can_manage_contracts_with_invalid_permission():
    payload = {"role": "viewer"}
    assert can_manage_contracts(payload) is False


def test_can_manage_contracts_with_missing_role():
    payload = {}
    assert can_manage_contracts(payload) is False


def test_can_manage_contracts_with_empty_payload():
    payload = {}
    assert can_manage_contracts(payload) is False


def test_can_manage_contracts_with_invalid_payload_type():
    with pytest.raises(TypeError):
        can_manage_contracts("not a dict")
