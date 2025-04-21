import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from cli.init_command import init_all

@pytest.fixture
def runner():
    return CliRunner()

def test_init_all_roles_and_admin_already_exist(runner):
    with patch("cli.init_command.RoleBL") as mock_role_bl_cls, \
         patch("cli.init_command.CollaboratorBL") as mock_collab_bl_cls, \
         patch("cli.init_command.click.echo") as mock_echo:

        mock_role_bl = MagicMock()
        mock_collab_bl = MagicMock()

        # simulate all roles already exist (by raising ValueError)
        mock_role_bl.create_role.side_effect = ValueError("Role already exists")
        mock_collab_bl.dal.get_by_email_raw.return_value = MagicMock()  # Admin already exists

        mock_role_bl_cls.return_value = mock_role_bl
        mock_collab_bl_cls.return_value = mock_collab_bl

        result = runner.invoke(init_all)

        assert result.exit_code == 0
        mock_echo.assert_any_call("Les rôles existent déjà.")
        mock_echo.assert_any_call("Un administrateur existe déjà.")

def test_init_all_creates_roles_and_admin_successfully(runner):
    with patch("cli.init_command.RoleBL") as mock_role_bl_cls, \
         patch("cli.init_command.CollaboratorBL") as mock_collab_bl_cls, \
         patch("cli.init_command.click.prompt", return_value="secureadminpwd"), \
         patch("cli.init_command.hash_password", return_value="hashedpwd"), \
         patch("cli.init_command.click.echo") as mock_echo:

        mock_role_bl = MagicMock()
        mock_collab_bl = MagicMock()

        # Simule que les rôles n'existent pas encore
        mock_role_bl.create_role.side_effect = [None, None, None]
        mock_role_bl.get_gestion_role.return_value = MagicMock(id=1)

        # Simule qu'aucun admin n'existe encore
        mock_collab_bl.dal.get_by_email_raw.return_value = None

        mock_role_bl_cls.return_value = mock_role_bl
        mock_collab_bl_cls.return_value = mock_collab_bl

        result = runner.invoke(init_all)

        assert result.exit_code == 0
        mock_echo.assert_any_call("Rôles crées : gestion, commercial, support")
        mock_echo.assert_any_call("Admin créé : admin@epicevents.fr")

def test_init_all_fails_if_gestion_role_missing(runner):
    with patch("cli.init_command.RoleBL") as mock_role_bl_cls, \
         patch("cli.init_command.CollaboratorBL") as mock_collab_bl_cls, \
         patch("cli.init_command.click.prompt", return_value="secureadminpwd"), \
         patch("cli.init_command.hash_password", return_value="hashedpwd"), \
         patch("cli.init_command.click.echo") as mock_echo:

        mock_role_bl = MagicMock()
        mock_collab_bl = MagicMock()

        mock_role_bl.create_role.side_effect = [None, None, None]
        mock_role_bl.get_gestion_role.return_value = None  # simulate missing gestion role
        mock_collab_bl.dal.get_by_email_raw.return_value = None

        mock_role_bl_cls.return_value = mock_role_bl
        mock_collab_bl_cls.return_value = mock_collab_bl

        result = runner.invoke(init_all)

        assert result.exit_code == 0
        mock_echo.assert_any_call("Rôle 'gestion' introuvable. Initialisation interrompue.")

def test_init_all_general_exception_handled(runner):
    with patch("cli.init_command.RoleBL", side_effect=Exception("DB down")), \
         patch("cli.init_command.click.echo") as mock_echo:

        result = runner.invoke(init_all)

        assert result.exit_code == 0
        mock_echo.assert_any_call("Erreur lors de l'initialisation : DB down")