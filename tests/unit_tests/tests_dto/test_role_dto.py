import pytest
from dtos.role_dto import RoleDTO


def test_role_dto_initialization():
    role = RoleDTO(id=1, name="Admin")
    assert role.id == 1
    assert role.name == "Admin"


def test_role_dto_id_type():
    role = RoleDTO(id=1, name="User")
    assert isinstance(role.id, int)


def test_role_dto_name_type():
    role = RoleDTO(id=2, name="Moderator")
    assert isinstance(role.name, str)


def test_role_dto_equality():
    role1 = RoleDTO(id=3, name="Viewer")
    role2 = RoleDTO(id=3, name="Viewer")
    assert role1 == role2


def test_role_dto_inequality():
    role1 = RoleDTO(id=4, name="User")
    role2 = RoleDTO(id=5, name="Admin")
    assert role1 != role2