from unittest.mock import MagicMock

import pytest
from dal.role_dal import RoleDAL
from dtos.role_dto import RoleDTO
from models.role import Role
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def role_dal(mock_session):
    return RoleDAL(mock_session)


@pytest.fixture
def sample_role():
    return Role(id=1, name="Admin")


@pytest.fixture
def sample_role_dto():
    return RoleDTO(id=1, name="Admin")


def test_get_by_name_returns_role_dto(role_dal, mock_session, sample_role, sample_role_dto):
    mock_session.query.return_value.filter_by.return_value.first.return_value = sample_role
    role_dal._to_dto = MagicMock(return_value=sample_role_dto)

    result = role_dal.get_by_name("Admin")

    assert result == sample_role_dto
    mock_session.query.assert_called_once_with(Role)
    mock_session.query.return_value.filter_by.assert_called_once_with(name="Admin")
    role_dal._to_dto.assert_called_once_with(sample_role)


def test_get_by_name_returns_none_when_role_not_found(role_dal, mock_session):
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    result = role_dal.get_by_name("NonExistentRole")

    assert result is None
    mock_session.query.assert_called_once_with(Role)
    mock_session.query.return_value.filter_by.assert_called_once_with(name="NonExistentRole")
