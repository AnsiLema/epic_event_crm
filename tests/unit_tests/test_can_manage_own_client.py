import pytest
from security.permissions import can_manage_own_clients


@pytest.mark.parametrize(
    "payload, expected",
    [
        ({"role": "commercial"}, True),  # Valid role that has permission
        ({"role": "admin"}, False),  # Role without permission
        ({"role": None}, False),  # Missing role
        ({}, False),  # Empty payload
        (None, False), # None payload, should raise TypeError
    ],
)
def test_can_manage_own_clients(payload, expected):
    if payload is None:
        with pytest.raises(TypeError):
            can_manage_own_clients(payload)  # Testing for TypeError
    else:
        assert can_manage_own_clients(payload) == expected
