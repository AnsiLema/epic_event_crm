import pytest
from dal.role_dal import RoleDAL
from dtos.role_dto import RoleDTO
from models.role import Role
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session(mocker):
    return mocker.Mock(spec=Session)


@pytest.fixture
def role_dal(mock_session):
    return RoleDAL(db=mock_session)


def test_to_dto_conversion(role_dal):
    role = Role(id=1, name="Admin")
    result = role_dal._to_dto(role)
    assert isinstance(result, RoleDTO)
    assert result.id == 1
    assert result.name == "Admin"


def test_to_dto_with_invalid_role(role_dal):
    with pytest.raises(AttributeError):
        role_dal._to_dto(None)
