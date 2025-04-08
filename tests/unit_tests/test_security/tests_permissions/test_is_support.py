import pytest
from security.permissions import is_support


def test_is_support_with_support_role():
    payload = {"role": "support"}
    assert is_support(payload) is True


def test_is_support_with_non_support_role():
    payload = {"role": "admin"}
    assert is_support(payload) is False


def test_is_support_with_missing_role_key():
    payload = {}
    assert is_support(payload) is False


def test_is_support_with_none_payload():
    payload = None
    with pytest.raises(TypeError):
        is_support(payload)


def test_is_support_with_empty_string_role():
    payload = {"role": ""}
    assert is_support(payload) is False
