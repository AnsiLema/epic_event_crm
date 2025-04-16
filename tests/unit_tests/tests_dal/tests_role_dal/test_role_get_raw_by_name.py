from unittest.mock import MagicMock
import pytest
from dal.role_dal import RoleDAL
from models.role import Role
from sqlalchemy.orm import Session


def test_get_raw_by_name_found(mocker):
    db_session = MagicMock(spec=Session)
    mock_role = Role(id=1, name="gestion")

    mock_query = mocker.MagicMock()
    mock_query.filter_by.return_value.first.return_value = mock_role
    db_session.query.return_value = mock_query

    role_dal = RoleDAL(db_session)
    result = role_dal.get_raw_by_name("gestion")

    assert result == mock_role
    db_session.query.assert_called_once_with(Role)
    mock_query.filter_by.assert_called_once_with(name="gestion")


def test_get_raw_by_name_not_found(mocker):
    db_session = MagicMock(spec=Session)

    mock_query = mocker.MagicMock()
    mock_query.filter_by.return_value.first.return_value = None
    db_session.query.return_value = mock_query

    role_dal = RoleDAL(db_session)
    result = role_dal.get_raw_by_name("non_existing_role")

    assert result is None
    db_session.query.assert_called_once_with(Role)
    mock_query.filter_by.assert_called_once_with(name="non_existing_role")
