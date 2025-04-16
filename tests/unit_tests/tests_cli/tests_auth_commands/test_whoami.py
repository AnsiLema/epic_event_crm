from unittest.mock import patch

import pytest
from cli.auth_commands import whoami
from click.testing import CliRunner


@patch("cli.auth_commands.load_token")
@patch("cli.auth_commands.decode_access_token")
def test_whoami_no_token(mock_decode_access_token, mock_load_token):
    mock_load_token.return_value = None
    runner = CliRunner()

    result = runner.invoke(whoami)

    assert result.exit_code == 0
    assert "Vous devez vous connecter." in result.output
    mock_decode_access_token.assert_not_called()


@patch("cli.auth_commands.load_token")
@patch("cli.auth_commands.decode_access_token")
def test_whoami_invalid_token(mock_decode_access_token, mock_load_token):
    mock_load_token.return_value = "invalid_token"
    mock_decode_access_token.return_value = None
    runner = CliRunner()

    result = runner.invoke(whoami)

    assert result.exit_code == 0
    assert "Token invalide ou expiré" in result.output


@patch("cli.auth_commands.load_token")
@patch("cli.auth_commands.decode_access_token")
def test_whoami_valid_token(mock_decode_access_token, mock_load_token):
    mock_load_token.return_value = "valid_token"
    mock_decode_access_token.return_value = {"email": "user@example.com", "role": "Admin"}
    runner = CliRunner()

    result = runner.invoke(whoami)

    assert result.exit_code == 0
    assert "👤 Connecté : user@example.com (rôle : Admin)" in result.output
