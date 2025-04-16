from click.testing import CliRunner
from cli.auth_commands import logout


def test_logout_success(mocker):
    # Corriger le patch au bon emplacement
    mock_delete_token = mocker.patch("cli.auth_commands.delete_token")
    runner = CliRunner()

    result = runner.invoke(logout)

    mock_delete_token.assert_called_once()
    assert result.exit_code == 0
    assert "Déconnecté avec succès." in result.output


def test_logout_file_not_found(mocker):
    # Patch au bon endroit + simulate FileNotFoundError
    mock_delete_token = mocker.patch("cli.auth_commands.delete_token", side_effect=FileNotFoundError)
    runner = CliRunner()

    result = runner.invoke(logout)

    mock_delete_token.assert_called_once()
    assert result.exit_code == 0
    assert "Déconnecté avec succès."
