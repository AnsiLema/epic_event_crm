from unittest.mock import MagicMock

import pytest
from bl.role_bl import RoleBL
from dtos.role_dto import RoleDTO


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def role_bl(mock_session):
    return RoleBL(db=mock_session)


@pytest.fixture
def mock_role_dal(role_bl):
    role_bl.dal = MagicMock()
    return role_bl.dal


def test_create_role_success(role_bl, mock_role_dal):
    """Test successful creation of a new role."""
    role_name = "Admin"
    created_role = RoleDTO(id=1, name=role_name)
    mock_role_dal.get_by_name.return_value = None
    mock_role_dal.create.return_value = created_role

    result = role_bl.create_role(name=role_name)

    mock_role_dal.get_by_name.assert_called_once_with(role_name)
    mock_role_dal.create.assert_called_once_with(role_name)
    assert result == created_role


def test_create_role_already_exists(role_bl, mock_role_dal):
    """Test creation of a role that already exists raises ValueError."""
    role_name = "Admin"
    existing_role = RoleDTO(id=1, name=role_name)
    mock_role_dal.get_by_name.return_value = existing_role

    with pytest.raises(ValueError, match=f"Le role {role_name} existe déja."):
        role_bl.create_role(name=role_name)

    mock_role_dal.get_by_name.assert_called_once_with(role_name)
    mock_role_dal.create.assert_not_called()
