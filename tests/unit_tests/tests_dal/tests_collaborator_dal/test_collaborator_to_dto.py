from unittest.mock import MagicMock

import pytest
from dal.collaborator_dal import CollaboratorDAL
from dtos.collaborator_dto import CollaboratorDTO
from models.collaborator import Collaborator
from sqlalchemy.orm import Session


def test_to_dto_valid_collaborator():
    mock_session = MagicMock(spec=Session)
    dal = CollaboratorDAL(db=mock_session)

    mock_role = MagicMock()
    mock_role.name = "Admin"

    collaborator = Collaborator(
        id=1,
        name="Jane Doe",
        email="jane.doe@example.com",
        role=mock_role
    )

    dto = dal._to_dto(collaborator)

    assert isinstance(dto, CollaboratorDTO)
    assert dto.id == 1
    assert dto.name == "Jane Doe"
    assert dto.email == "jane.doe@example.com"
    assert dto.role_name == "Admin"


def test_to_dto_null_role():
    mock_session = MagicMock(spec=Session)
    dal = CollaboratorDAL(db=mock_session)

    collaborator = Collaborator(
        id=2,
        name="John Doe",
        email="john.doe@example.com",
        role=None
    )

    with pytest.raises(AttributeError):
        dal._to_dto(collaborator)
