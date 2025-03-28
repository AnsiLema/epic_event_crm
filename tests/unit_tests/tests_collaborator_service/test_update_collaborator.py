from unittest.mock import Mock
import pytest
from models.collaborator import Collaborator
from models.role import Role
from security.password import hash_password
from security.permissions import can_manage_collaborators
from services.collaborator_service import update_collaborator
from sqlalchemy.orm import Session



@pytest.fixture
def db_session():
    return Mock(spec=Session)


@pytest.fixture
def sample_collaborator():
    return Mock(spec=Collaborator, id=1, name="John Doe", email="john@example.com", password="hashed_password")


@pytest.fixture
def sample_role():
    return Mock(spec=Role, id=1, name="gestion")


@pytest.fixture
def payload_with_permission():
    return {"role": "gestion"}


@pytest.fixture
def payload_without_permission():
    return {"role": "support"}


def test_update_collaborator_successfully(db_session, sample_collaborator, sample_role, payload_with_permission):
    db_session.query.return_value.filter_by.return_value.first.side_effect = [sample_collaborator, sample_role]

    sample_collaborator.role = sample_role

    result = update_collaborator(
        db=db_session,
        payload=payload_with_permission,
        collaborator_id=1,
        new_name="Jane Doe",
        new_email="jane@example.com",
        new_password="new_password",
        new_role_name="gestion"
    )

    assert result == sample_collaborator
    assert sample_collaborator.name == "Jane Doe"
    assert sample_collaborator.email == "jane@example.com"
    assert sample_collaborator.role == sample_role
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(sample_collaborator)



def test_update_collaborator_no_permission(db_session, payload_without_permission):
    db_session.query.return_value.filter_by.return_value.first.return_value = None

    result = update_collaborator(
        db=db_session,
        payload=payload_without_permission,
        collaborator_id=1,
        new_name="Jane Doe"
    )

    assert result is None
    db_session.commit.assert_not_called()


def test_update_nonexistent_collaborator(db_session, payload_with_permission):
    db_session.query.return_value.filter_by.return_value.first.return_value = None

    result = update_collaborator(
        db=db_session,
        payload=payload_with_permission,
        collaborator_id=999,
        new_name="Jane Doe"
    )

    assert result is None
    db_session.commit.assert_not_called()


def test_update_collaborator_invalid_role(db_session, sample_collaborator, payload_with_permission):
    db_session.query.return_value.filter_by.return_value.first.side_effect = [sample_collaborator, None]

    result = update_collaborator(
        db=db_session,
        payload=payload_with_permission,
        collaborator_id=1,
        new_role_name="invalid_role"
    )

    assert result is None
    db_session.commit.assert_not_called()


def test_update_collaborator_partial_update(db_session, sample_collaborator, payload_with_permission):
    db_session.query.return_value.filter_by.return_value.first.return_value = sample_collaborator

    result = update_collaborator(
        db=db_session,
        payload=payload_with_permission,
        collaborator_id=1,
        new_name="Jane Doe"
    )

    assert result == sample_collaborator
    assert sample_collaborator.name == "Jane Doe"
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(sample_collaborator)
