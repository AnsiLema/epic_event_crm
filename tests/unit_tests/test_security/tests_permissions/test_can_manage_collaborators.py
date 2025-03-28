# File: tests/test_permissions.py

import pytest
from security.permissions import can_manage_collaborators


def test_can_manage_collaborators_with_valid_role():
    payload = {"role": "gestion"}
    assert can_manage_collaborators(payload) is True


def test_can_manage_collaborators_with_invalid_role():
    payload = {"role": "viewer"}
    assert can_manage_collaborators(payload) is False


def test_can_manage_collaborators_with_no_role():
    payload = {}
    assert can_manage_collaborators(payload) is False


def test_can_manage_collaborators_with_invalid_payload_type():
    with pytest.raises(TypeError):
        can_manage_collaborators("invalid_payload")


def test_can_manage_collaborators_with_none_role():
    payload = {"role": None}
    assert can_manage_collaborators(payload) is False


def test_can_manage_collaborators_with_additional_payload_data():
    payload = {"role": "gestion", "additional_info": "extra_data"}
    assert can_manage_collaborators(payload) is True
