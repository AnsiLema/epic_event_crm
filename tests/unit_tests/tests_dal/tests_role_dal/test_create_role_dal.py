from unittest.mock import MagicMock

import pytest
from dal.role_dal import RoleDAL
from dtos.role_dto import RoleDTO
from models.role import Role
from sqlalchemy.orm import Session


@pytest.fixture
def db_session_mock():
    return MagicMock(spec=Session)


@pytest.fixture
def role_dal(db_session_mock):
    return RoleDAL(db=db_session_mock)


def test_create_role_success(role_dal, db_session_mock):
    # Arrange
    role_name = "gestion"
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.side_effect = lambda obj: setattr(obj, "id", 1)
    role_dal._to_dto = MagicMock(return_value=RoleDTO(id=1, name=role_name))

    # Act
    result = role_dal.create_role(name=role_name)

    # Assert
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once()

    # Vérifie que le bon objet Role a été passé à .add()
    added_role = db_session_mock.add.call_args.args[0]
    assert isinstance(added_role, Role)
    assert added_role.name == role_name

    assert isinstance(result, RoleDTO)
    assert result.name == role_name
    assert result.id == 1


def test_create_role_invalid_name(role_dal, db_session_mock):
    # Arrange
    db_session_mock.commit.side_effect = Exception("Integrity Error")

    # Act & Assert
    with pytest.raises(Exception, match="Integrity Error"):
        role_dal.create_role(name="invalid")

    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()


def test_create_role_empty_name(role_dal, db_session_mock):
    with pytest.raises(ValueError, match="Le nom du rôle ne peut être vide."):
        role_dal.create_role(name="")

    db_session_mock.add.assert_not_called()
    db_session_mock.commit.assert_not_called()
