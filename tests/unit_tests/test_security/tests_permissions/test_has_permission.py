import pytest
from security.permissions import has_permission


def test_has_permission_with_valid_role():
    payload = {"role": "admin"}
    allowed_roles = ["admin", "editor"]
    assert has_permission(payload, allowed_roles) is True


def test_has_permission_with_invalid_role():
    payload = {"role": "guest"}
    allowed_roles = ["admin", "editor"]
    assert has_permission(payload, allowed_roles) is False


def test_has_permission_missing_role_key():
    payload = {}
    allowed_roles = ["admin", "editor"]
    assert has_permission(payload, allowed_roles) is False


def test_has_permission_with_invalid_payload_type():
    payload = ["invalid", "payload"]
    allowed_roles = ["admin", "editor"]
    with pytest.raises(TypeError):
        has_permission(payload, allowed_roles)


def test_has_permission_with_empty_allowed_roles():
    payload = {"role": "admin"}
    allowed_roles = []
    assert has_permission(payload, allowed_roles) is False


def test_has_permission_with_none_as_payload():
    payload = None
    allowed_roles = ["admin", "editor"]
    with pytest.raises(TypeError):
        has_permission(payload, allowed_roles)


def test_has_permission_role_not_in_allowed_roles():
    payload = {"role": "manager"}
    allowed_roles = ["admin", "editor", "viewer"]
    assert has_permission(payload, allowed_roles) is False
