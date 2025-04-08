import pytest
from security.permissions import is_commercial


def test_is_commercial_with_commercial_role():
    payload = {"role": "commercial"}
    assert is_commercial(payload) is True


def test_is_commercial_with_non_commercial_role():
    payload = {"role": "non-commercial"}
    assert is_commercial(payload) is False


def test_is_commercial_with_no_role_key():
    payload = {"other_key": "value"}
    assert is_commercial(payload) is False


def test_is_commercial_with_empty_payload():
    payload = {}
    assert is_commercial(payload) is False


def test_is_commercial_with_invalid_type_payload():
    with pytest.raises(TypeError):
        is_commercial("pas un dictionnaire")


def test_is_commercial_with_role_as_none():
    payload = {"role": None}
    assert is_commercial(payload) is False