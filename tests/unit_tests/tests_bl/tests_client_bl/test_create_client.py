import unittest
from datetime import date
from unittest.mock import MagicMock

import pytest
from bl.client_bl import ClientBLL
from dal.client_dal import ClientDAL
from dal.collaborator_dal import CollaboratorDAL
from dtos.client_dto import ClientDTO
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_client_dal(mock_db):
    return MagicMock(ClientDAL(mock_db))


@pytest.fixture
def mock_collaborator_dal(mock_db):
    return MagicMock(CollaboratorDAL(mock_db))


@pytest.fixture
def client_bll(mock_db, mock_client_dal, mock_collaborator_dal):
    instance = ClientBLL(mock_db)
    instance.dal = mock_client_dal
    instance.collaborator_dal = mock_collaborator_dal
    return instance


@pytest.fixture
def current_user_commercial():
    return {"sub": "user@example.com", "role": "commercial"}


@pytest.fixture
def current_user_non_commercial():
    return {"sub": "user@example.com", "role": "admin"}


class TestClientBLL(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_client_dal = MagicMock(ClientDAL(self.mock_db))
        self.mock_collaborator_dal = MagicMock(CollaboratorDAL(self.mock_db))
        self.client_bll = ClientBLL(self.mock_db)
        self.client_bll.dal = self.mock_client_dal
        self.client_bll.collaborator_dal = self.mock_collaborator_dal
        self.current_user_commercial = {"sub": "user@example.com", "role": "commercial"}
        self.current_user_non_commercial = {"sub": "user@example.com", "role": "admin"}

    def test_create_client_success(self):
        self.mock_collaborator_dal.get_by_email_raw.return_value = MagicMock(id=1)
        self.mock_client_dal.create.return_value = MagicMock(ClientDTO)

        data = {"name": "Test Client", "email": "test@example.com"}
        response = self.client_bll.create_client(data, self.current_user_commercial)

        self.assertEqual(response, self.mock_client_dal.create.return_value)
        self.assertEqual(data["commercial_id"], 1)
        self.assertEqual(data["creation_date"], date.today())

    def test_create_client_not_commercial(self):
        data = {"name": "Test Client", "email": "test@example.com"}
        with self.assertRaises(PermissionError):
            self.client_bll.create_client(data, self.current_user_non_commercial)

    def test_create_client_from_input_existing_email(self):
        self.mock_client_dal.get_by_email.return_value = MagicMock(ClientDTO)

        with self.assertRaises(ValueError):
            self.client_bll.create_client_from_input("Test Client", "test@example.com", "123456789",
                                                     "Test Company", self.current_user_commercial)

    def test_update_client_success(self):
        self.mock_collaborator_dal.get_by_email_raw.return_value = MagicMock(id=1)
        self.mock_client_dal.get.return_value = MagicMock(commercial_id=1)
        self.mock_client_dal.update_by_id.return_value = MagicMock(ClientDTO)

        updates = {"name": "Updated Client"}
        response = self.client_bll.update_client(1, updates, self.current_user_commercial)

        self.assertEqual(response, self.mock_client_dal.update_by_id.return_value)
        self.mock_client_dal.get.assert_called_once_with(1)
        self.mock_client_dal.update_by_id.assert_called_once_with(1, updates)

    def test_update_client_not_found(self):
        self.mock_collaborator_dal.get_by_email_raw.return_value = MagicMock(id=1)
        self.mock_client_dal.get.return_value = None

        with self.assertRaises(ValueError):
            self.client_bll.update_client(1, {}, self.current_user_commercial)

    def test_get_all_clients(self):
        self.mock_client_dal.get_all.return_value = [MagicMock(ClientDTO)]

        response = self.client_bll.get_all_clients()

        self.assertEqual(response, self.mock_client_dal.get_all.return_value)

    def test_get_client_by_id_success(self):
        self.mock_client_dal.get.return_value = MagicMock(ClientDTO)

        response = self.client_bll.get_client(1)

        self.assertEqual(response, self.mock_client_dal.get.return_value)
        self.mock_client_dal.get.assert_called_once_with(1)

    def test_get_client_by_id_not_found(self):
        self.mock_client_dal.get.return_value = None

        with self.assertRaises(ValueError):
            self.client_bll.get_client(1)
