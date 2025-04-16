import pytest
from unittest.mock import patch, MagicMock
from cli.client_commands import create_client


@pytest.fixture
def token_patches():
    with patch("cli.auth_decorator.load_token", return_value="fake-token"), \
         patch("cli.auth_decorator.decode_access_token", return_value={"id": 1, "sub": "user@example.com", "role": "commercial"}):
        yield


def test_create_client_success(token_patches):
    with patch("cli.client_commands.Session"), \
         patch("cli.client_commands.ClientBLL") as mock_client_bll, \
         patch("click.echo") as mock_echo:

        mock_client = MagicMock()
        mock_client.name = "Test Client"
        mock_client.email = "test@example.com"
        mock_client_bll.return_value.create_client_from_input.return_value = mock_client

        # Appel direct sans current_user
        create_client.callback(
            name="Test Client",
            email="test@example.com",
            phone="",
            company=""
        )

        mock_echo.assert_called_once_with("Client créé : Test Client (test@example.com)")
        mock_client_bll.return_value.create_client_from_input.assert_called_once()


def test_create_client_missing_email(token_patches):
    with patch("cli.client_commands.Session"), \
         patch("cli.client_commands.ClientBLL") as mock_client_bll, \
         patch("click.echo") as mock_echo:

        mock_client_bll.return_value.create_client_from_input.side_effect = ValueError("Le nom et l'email sont requis.")

        create_client.callback(
            name="Test Client",
            email="",
            phone="",
            company=""
        )

        mock_echo.assert_called_once_with("Erreur : Le nom et l'email sont requis.")


def test_create_client_duplicate_email(token_patches):
    with patch("cli.client_commands.Session"), \
         patch("cli.client_commands.ClientBLL") as mock_client_bll, \
         patch("click.echo") as mock_echo:

        mock_client_bll.return_value.create_client_from_input.side_effect = ValueError("Un client avec cet email existe déjà.")

        create_client.callback(
            name="Test Client",
            email="duplicate@example.com",
            phone="",
            company=""
        )

        mock_echo.assert_called_once_with("Erreur : Un client avec cet email existe déjà.")