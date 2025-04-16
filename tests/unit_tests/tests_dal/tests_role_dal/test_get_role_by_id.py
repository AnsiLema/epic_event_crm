from unittest.mock import Mock

import pytest
from dal.role_dal import RoleDAL
from dtos.role_dto import RoleDTO
from models.role import Role
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    return Mock(spec=Session)


@pytest.fixture
def role_dal(mock_session):
    return RoleDAL(db=mock_session)


def test_get_by_id_existing_role(role_dal, mock_session):
    mock_role = Role(id=1, name="Admin")
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_role

    result = role_dal.get_by_id(1)

    assert result == RoleDTO(id=1, name="Admin")


def test_get_by_id_nonexistent_role(role_dal, mock_session):
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    result = role_dal.get_by_id(999)

    assert result is None
