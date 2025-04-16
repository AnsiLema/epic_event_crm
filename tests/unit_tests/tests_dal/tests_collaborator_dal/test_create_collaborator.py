import pytest
from dal.collaborator_dal import CollaboratorDAL
from dtos.collaborator_dto import CollaboratorDTO
from models.collaborator import Collaborator
from sqlalchemy.orm import Session


@pytest.fixture
def db_session(mocker):
    return mocker.MagicMock(spec=Session)


@pytest.fixture
def collaborator_dal(db_session):
    return CollaboratorDAL(db=db_session)


def test_create_new_collaborator(collaborator_dal, db_session, mocker):
    data = {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "password123",
        "role_id": 2,
    }
    collaborator = mocker.MagicMock(spec=Collaborator)
    collaborator.id = 1
    collaborator.name = data["name"]
    collaborator.email = data["email"]
    collaborator.role_id = data["role_id"]

    mocker.patch("dal.collaborator_dal.Collaborator", return_value=collaborator)
    collaborator_dal._to_dto = mocker.MagicMock(return_value=CollaboratorDTO(
        id=1, name="John Doe", email="john.doe@example.com", role_name="Role"
    ))

    result = collaborator_dal.create(data)

    db_session.add.assert_called_once_with(collaborator)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(collaborator)

    assert isinstance(result, CollaboratorDTO)
    assert result.id == 1
    assert result.name == "John Doe"
    assert result.email == "john.doe@example.com"
    assert result.role_name == "Role"
