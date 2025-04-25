from types import SimpleNamespace

import pytest
from unittest.mock import patch, MagicMock
from cli.client_commands import list_clients


@pytest.fixture
def token_patches():
    with patch("cli.auth_decorator.load_token", return_value="fake-token"), \
         patch("cli.auth_decorator.decode_access_token", return_value={"id": 1,
                                                                       "sub": "user@example.com",
                                                                       "role": "commercial"}):
        yield


def test_list_clients_success(token_patches):
    client1 = SimpleNamespace(id=1, name="Client One", email="client1@example.com", company="Company A")
    client2 = SimpleNamespace(id=2, name="Client Two", email="client2@example.com", company=None)

    with patch("cli.client_commands.Session"), \
         patch("cli.client_commands.ClientBLL") as mock_bll, \
         patch("click.echo") as mock_echo:

        mock_bll.return_value.get_all_clients.return_value = [client1, client2]

        list_clients.callback()

        mock_echo.assert_any_call("Client One - client1@example.com | Company A | Id : 1")
        mock_echo.assert_any_call("Client Two - client2@example.com | Non renseigné | Id : 2")
        assert mock_echo.call_count == 2


def test_list_clients_empty(token_patches):
    with patch("cli.client_commands.Session"), \
         patch("cli.client_commands.ClientBLL") as mock_bll, \
         patch("click.echo") as mock_echo:

        mock_bll.return_value.get_all_clients.return_value = []

        list_clients.callback()

        mock_echo.assert_called_once_with("Aucun client trouvé.")


def test_list_clients_failure(token_patches):
    with patch("cli.client_commands.Session"), \
         patch("cli.client_commands.ClientBLL") as mock_bll, \
         patch("click.echo") as mock_echo:

        mock_bll.return_value.get_all_clients.side_effect = Exception("Database error")

        list_clients.callback()

        mock_echo.assert_called_once_with("Erreur : Database error")