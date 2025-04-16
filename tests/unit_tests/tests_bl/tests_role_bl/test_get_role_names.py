from unittest.mock import MagicMock

import pytest
from bl.role_bl import RoleBL
from dtos.role_dto import RoleDTO
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    """Fixture for providing a mocked database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_role_bl(mock_db):
    """Fixture for providing a RoleBL instance with a mocked database session."""
    return RoleBL(mock_db)


def test_get_role_by_name_valid(mock_role_bl, mock_db):
    """Test successfully fetching a role by name."""
    mock_role = RoleDTO(id=1, name="Admin")
    mock_role_bl.dal.get_by_name = MagicMock(return_value=mock_role)

    result = mock_role_bl.get_role_by_name("Admin")

    assert result == mock_role
    mock_role_bl.dal.get_by_name.assert_called_once_with("Admin")


def test_get_role_by_name_not_found(mock_role_bl, mock_db):
    """Test fetching a non-existent role by name raises a ValueError."""
    mock_role_bl.dal.get_by_name = MagicMock(return_value=None)

    with pytest.raises(ValueError, match="Role introuvable."):
        mock_role_bl.get_role_by_name("NonExistentRole")

    mock_role_bl.dal.get_by_name.assert_called_once_with("NonExistentRole")
