import click
import pytest
from cli.auth_commands import require_auth


def test_require_auth_valid_token(mocker):
    # Patch les fonctions telles qu'utilisées DANS cli.auth_commands
    mocker.patch("cli.auth_commands.load_token", return_value="valid_token")
    mocker.patch("cli.auth_commands.decode_access_token", return_value={"user_id": 1})

    result = require_auth()

    assert result == {"user_id": 1}


def test_require_auth_no_token(mocker):
    mocker.patch("cli.auth_commands.load_token", return_value=None)

    with pytest.raises(click.ClickException) as excinfo:
        require_auth()

    assert str(excinfo.value) == "Vous devez vous connecter."


def test_require_auth_invalid_token(mocker):
    mocker.patch("cli.auth_commands.load_token", return_value="invalid_token")
    mocker.patch("cli.auth_commands.decode_access_token", return_value=None)

    with pytest.raises(click.ClickException) as excinfo:
        require_auth()

    assert str(excinfo.value) == "Token Invalide ou expiré."