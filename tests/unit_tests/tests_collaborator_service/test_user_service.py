from unittest.mock import MagicMock

import pytest
from models.collaborator import Collaborator
from models.role import Role
from services.user_service import create_collaborator
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def mock_db_session():
    mock_session = MagicMock()
    return mock_session


def test_create_collaborator_success(mock_db_session):
    test_name = "John Doe"
    test_email = "john.doe@example.com"
    test_password = "securepassword"
    test_role_name = "gestion"

    mock_role = Role(id=1, name=test_role_name)
    mock_db_session.query.return_value.filter_by.return_value.first.side_effect = [
        None,  # No existing user
        mock_role,  # Role found
    ]

    collaborator = create_collaborator(
        db=mock_db_session,
        name=test_name,
        email=test_email,
        password=test_password,
        role_name=test_role_name,
    )

    assert collaborator is not None
    assert collaborator.name == test_name
    assert collaborator.email == test_email
    assert collaborator.role == mock_role
    mock_db_session.add.assert_called_once_with(collaborator)
    mock_db_session.commit.assert_called_once()


def test_create_collaborator_missing_fields(mock_db_session):
    collaborator = create_collaborator(
        db=mock_db_session, name=None, email=None, password=None, role_name=None
    )

    assert collaborator is None
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_create_collaborator_existing_email(mock_db_session):
    mock_existing_user = Collaborator(
        id=1, name="Existing User", email="existing@example.com", password="hashed_pw"
    )
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = (
        mock_existing_user
    )

    collaborator = create_collaborator(
        db=mock_db_session,
        name="John Doe",
        email="existing@example.com",
        password="securepassword",
        role_name="gestion",
    )

    # Assert
    assert collaborator is None
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_create_collaborator_role_not_found(mock_db_session):
    mock_db_session.query.return_value.filter_by.return_value.first.side_effect = [
        None,  # No existing user
        None,  # Role not found
    ]

    collaborator = create_collaborator(
        db=mock_db_session,
        name="John Doe",
        email="john.doe@example.com",
        password="securepassword",
        role_name="nonexistent_role",
    )

    assert collaborator is None
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_create_collaborator_integrity_error(mock_db_session):
    mock_db_session.query.return_value.filter_by.return_value.first.side_effect = [
        None,  # No existing user
        Role(id=1, name="gestion"),  # Role found
    ]
    mock_db_session.add.side_effect = IntegrityError("Integrity error", None, None)

    collaborator = create_collaborator(
        db=mock_db_session,
        name="John Doe",
        email="john.doe@example.com",
        password="securepassword",
        role_name="gestion",
    )

    assert collaborator is None
    mock_db_session.commit.assert_not_called()

def test_create_collaborator_weak_password(mock_db_session):

    collaborator = create_collaborator(
        db=mock_db_session,
        name="John Doe",
        email="john.doe@example.com",
        password="short",  # 5 caractères
        role_name="gestion",
    )

    assert collaborator is None
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()

def test_create_collaborator_unexpected_exception(mock_db_session):
    mock_db_session.query.return_value.filter_by.return_value.first.side_effect = [
        None,           # No existing user
        Role(id=1, name="gestion"),  # Role found
    ]

    mock_db_session.add.side_effect = Exception("boom")

    collaborator = create_collaborator(
        db=mock_db_session,
        name="John Doe",
        email="john.doe@example.com",
        password="securepassword",
        role_name="gestion",
    )

    assert collaborator is None
    # Vérifie qu'on a bien rollback
    mock_db_session.rollback.assert_called_once()
    # Pas de commit puisque l'exception a été levée
    mock_db_session.commit.assert_not_called()
