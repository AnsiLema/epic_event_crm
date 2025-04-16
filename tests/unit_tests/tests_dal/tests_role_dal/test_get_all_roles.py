from unittest.mock import MagicMock

import pytest
from dal.role_dal import RoleDAL
from dtos.role_dto import RoleDTO
from models.role import Role


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def role_dal(mock_session):
    return RoleDAL(db=mock_session)


def test_get_all_no_roles(role_dal, mock_session):
    mock_session.query.return_value.all.return_value = []

    result = role_dal.get_all()

    assert result == []
    mock_session.query.assert_called_once_with(Role)
    mock_session.query().all.assert_called_once()


def test_get_all_with_roles(role_dal, mock_session, mocker):
    mock_role = Role(id=1, name="Admin")
    mock_session.query.return_value.all.return_value = [mock_role]
    mock_to_dto = mocker.patch.object(role_dal, "_to_dto", return_value=RoleDTO(id=1, name="Admin"))

    result = role_dal.get_all()

    assert len(result) == 1
    assert result[0] == RoleDTO(id=1, name="Admin")
    mock_session.query.assert_called_once_with(Role)
    mock_session.query().all.assert_called_once()
    mock_to_dto.assert_called_once_with(mock_role)


def test_get_all_multiple_roles(role_dal, mock_session, mocker):
    mock_roles = [
        Role(id=1, name="Admin"),
        Role(id=2, name="User"),
        Role(id=3, name="Guest")
    ]
    mock_session.query.return_value.all.return_value = mock_roles
    mock_to_dto = mocker.patch.object(
        role_dal,
        "_to_dto",
        side_effect=[
            RoleDTO(id=1, name="Admin"),
            RoleDTO(id=2, name="User"),
            RoleDTO(id=3, name="Guest")
        ]
    )

    result = role_dal.get_all()

    assert len(result) == 3
    assert result == [
        RoleDTO(id=1, name="Admin"),
        RoleDTO(id=2, name="User"),
        RoleDTO(id=3, name="Guest")
    ]
    mock_session.query.assert_called_once_with(Role)
    mock_session.query().all.assert_called_once()
    assert mock_to_dto.call_count == 3
    mock_to_dto.assert_any_call(mock_roles[0])
    mock_to_dto.assert_any_call(mock_roles[1])
    mock_to_dto.assert_any_call(mock_roles[2])
