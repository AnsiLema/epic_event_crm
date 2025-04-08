from unittest.mock import MagicMock, patch
from security.auth_service import authenticate_collaborator


class FakeRole:
    def __init__(self, name):
        self.name = name


class FakeUser:
    def __init__(self, id, email, password, role_name):
        self.id = id
        self.email = email
        self.password = password
        self.role = FakeRole(role_name)


def test_authenticate_success(monkeypatch):
    fake_user = FakeUser(id=1, email="bob@example.com", password="hashedpw", role_name="commercial")

    # Simulates DAL.get_by_email_raw()
    dal_mock = MagicMock()
    dal_mock.get_by_email_raw.return_value = fake_user

    db = MagicMock()
    monkeypatch.setattr("security.auth_service.CollaboratorDAL", lambda db: dal_mock)

    # Simulates hash checker (mock returns True)
    with patch("security.auth_service.verify_password", return_value=True):
        result = authenticate_collaborator(db, "bob@example.com", "correct_password")
        assert result == {
            "id": 1,
            "email": "bob@example.com",
            "role": "commercial"
        }


def test_authenticate_wrong_password(monkeypatch):
    fake_user = FakeUser(id=1, email="bob@example.com", password="hashedpw", role_name="commercial")

    dal_mock = MagicMock()
    dal_mock.get_by_email_raw.return_value = fake_user

    db = MagicMock()
    monkeypatch.setattr("security.auth_service.CollaboratorDAL", lambda db: dal_mock)

    # Simulates a wrong password
    with patch("security.auth_service.verify_password", return_value=False):
        result = authenticate_collaborator(db, "bob@example.com", "wrong_password")
        assert result is None


def test_authenticate_user_not_found(monkeypatch):
    dal_mock = MagicMock()
    dal_mock.get_by_email_raw.return_value = None

    db = MagicMock()
    monkeypatch.setattr("security.auth_service.CollaboratorDAL", lambda db: dal_mock)

    result = authenticate_collaborator(db, "unknown@example.com", "any")
    assert result is None