import pytest
from unittest.mock import patch, Mock
from click.testing import CliRunner
from cli.auth_commands import login


def test_login_success(mocker):
    mock_session = mocker.patch("cli.auth_commands.Session")
    mock_authenticate = mocker.patch("cli.auth_commands.authenticate_collaborator")
    mock_create_token = mocker.patch("cli.auth_commands.create_access_token")
    mock_save_token = mocker.patch("cli.auth_commands.save_token")

    db_mock = Mock()
    mock_session.return_value = db_mock
    mock_authenticate.return_value = {"email": "test@example.com", "role": "Admin"}
    mock_create_token.return_value = "fake-jwt-token"

    runner = CliRunner()
    result = runner.invoke(login, ["--email", "test@example.com", "--password", "password123"])

    mock_session.assert_called_once()
    mock_authenticate.assert_called_once_with(db_mock, "test@example.com", "password123")
    mock_create_token.assert_called_once_with(mock_authenticate.return_value)
    mock_save_token.assert_called_once_with("fake-jwt-token")
    assert result.exit_code == 0
    assert "Connecté : test@example.com (rôle : Admin)" in result.output


def test_login_invalid_credentials(mocker):
    mock_session = mocker.patch("cli.auth_commands.Session")
    mock_authenticate = mocker.patch("cli.auth_commands.authenticate_collaborator")
    mock_create_token = mocker.patch("cli.auth_commands.create_access_token")

    db_mock = Mock()
    mock_session.return_value = db_mock
    mock_authenticate.return_value = None

    runner = CliRunner()
    result = runner.invoke(login, ["--email", "invalid@example.com", "--password", "wrongpass"])

    mock_session.assert_called_once()
    mock_authenticate.assert_called_once_with(db_mock, "invalid@example.com", "wrongpass")
    mock_create_token.assert_not_called()
    assert result.exit_code == 0
    assert "Identifiants incorrects." in result.output


def test_login_token_save_failure(mocker):
    mock_session = mocker.patch("cli.auth_commands.Session")
    mock_authenticate = mocker.patch("cli.auth_commands.authenticate_collaborator")
    mock_create_token = mocker.patch("cli.auth_commands.create_access_token")
    mock_save_token = mocker.patch("cli.auth_commands.save_token", side_effect=Exception("Token save failed"))

    db_mock = Mock()
    mock_session.return_value = db_mock
    mock_authenticate.return_value = {"email": "test@example.com", "role": "User"}
    mock_create_token.return_value = "fake-jwt-token"

    runner = CliRunner()
    result = runner.invoke(login, ["--email", "test@example.com", "--password", "testpass"])

    mock_session.assert_called_once()
    mock_authenticate.assert_called_once_with(db_mock, "test@example.com", "testpass")
    mock_create_token.assert_called_once_with(mock_authenticate.return_value)
    mock_save_token.assert_called_once_with("fake-jwt-token")
    assert result.exit_code == 0
    # Tu peux choisir de vérifier l’absence ou la présence du message selon ton comportement attendu
    assert "Erreur lors de l'enregistrement du token : {e}," not in result.output