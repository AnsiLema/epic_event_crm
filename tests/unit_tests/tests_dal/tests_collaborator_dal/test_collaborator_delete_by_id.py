from unittest.mock import MagicMock

import pytest
from dal.collaborator_dal import CollaboratorDAL
from models.collaborator import Collaborator
from sqlalchemy.orm import Session


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def collaborator_dal(db_session):
    return CollaboratorDAL(db=db_session)


def test_delete_by_id_existing_collaborator(collaborator_dal, db_session):
    mock_collaborator = MagicMock(spec=Collaborator)
    db_session.query().filter_by().first.return_value = mock_collaborator

    result = collaborator_dal.delete_by_id(1)

    db_session.delete.assert_called_once_with(mock_collaborator)
    db_session.commit.assert_called_once()
    assert result is True


def test_delete_by_id_non_existing_collaborator(collaborator_dal, db_session):
    db_session.query().filter_by().first.return_value = None

    result = collaborator_dal.delete_by_id(1)

    db_session.delete.assert_not_called()
    db_session.commit.assert_not_called()
    assert result is False


def test_delete_by_id_db_exception(collaborator_dal, db_session):
    db_session.query().filter_by().first.side_effect = Exception("DB error")

    with pytest.raises(Exception, match="DB error"):
        collaborator_dal.delete_by_id(1)
