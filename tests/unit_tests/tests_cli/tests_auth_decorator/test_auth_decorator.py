from unittest.mock import patch, Mock

import pytest
from cli.auth_decorator import with_auth_payload
from click import ClickException


def test_with_auth_payload_valid_token(mocker):
    mocker.patch("cli.auth_decorator.load_token", return_value="valid_token")
    mocker.patch("cli.auth_decorator.decode_access_token", return_value={"user_id": 1})

    @with_auth_payload
    def dummy_function(*args, **kwargs):
        return kwargs.get("current_user")

    result = dummy_function()
    assert result == {"user_id": 1}


def test_with_auth_payload_no_token(mocker):
    mocker.patch("cli.auth_decorator.load_token", return_value=None)

    @with_auth_payload
    def dummy_function(*args, **kwargs):
        pass

    with pytest.raises(ClickException) as exc_info:
        dummy_function()
    assert "Vous devez être connecté(e)." in str(exc_info.value)


def test_with_auth_payload_invalid_token(mocker):
    mocker.patch("cli.auth_decorator.load_token", return_value="invalid_token")
    mocker.patch("cli.auth_decorator.decode_access_token", return_value=None)

    @with_auth_payload
    def dummy_function(*args, **kwargs):
        pass

    with pytest.raises(ClickException) as exc_info:
        dummy_function()
    assert "Token invalide ou expiré." in str(exc_info.value)
