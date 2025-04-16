from unittest.mock import MagicMock

import pytest
from bl.role_bl import RoleBL
from dtos.role_dto import RoleDTO


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def mock_role_dal(mock_session):
    mock_dal = MagicMock()
    mock_dal.get_all.return_value = [
        RoleDTO(id=1, name="Admin"),
        RoleDTO(id=2, name="User"),
    ]
    return mock_dal


@pytest.fixture
def role_bl(mock_session, mock_role_dal):
    role_bl_instance = RoleBL(mock_session)
    role_bl_instance.dal = mock_role_dal
    return role_bl_instance


def test_list_roles(role_bl):
    roles = role_bl.list_roles()
    assert len(roles) == 2
    assert roles[0].id == 1
    assert roles[0].name == "Admin"
    assert roles[1].id == 2
    assert roles[1].name == "User"
