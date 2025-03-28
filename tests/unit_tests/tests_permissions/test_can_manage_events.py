import pytest
from security.permissions import can_manage_events


@pytest.mark.parametrize("payload, expected", [
    ({"role": "gestion"}, True),  # User has one of the required roles
    ({"role": "support"}, True),  # User has the other required role
    ({"role": "admin"}, False),  # User has a role not in the required roles
    ({"role": None}, False),  # Role is explicitly set to None
    ({}, False),  # Payload lacks a role
])
def test_can_manage_events_valid_cases(payload, expected):
    assert can_manage_events(payload) == expected


def test_can_manage_events_invalid_payload():
    with pytest.raises(TypeError):
        can_manage_events("not_a_dict")  # Invalid payload type (not a dict)
