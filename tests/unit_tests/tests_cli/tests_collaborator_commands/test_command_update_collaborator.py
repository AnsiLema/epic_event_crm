from click.testing import CliRunner
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest


import cli.collaborator_commands as cc

_outer = cc.update_collaborator.callback
_inner = _outer.__wrapped__                        # fonction métier réelle

def bypass_auth(collaborator_id, *args, **kwargs):
    return _inner(collaborator_id, current_user={"id": 1, "role": "admin"})

cc.update_collaborator.callback = bypass_auth      # patch définitif


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()

@pytest.fixture(autouse=True)
def patch_session():
    with patch("cli.collaborator_commands.Session") as s_cls:
        s_cls.return_value = MagicMock()
        yield s_cls

@pytest.fixture
def bl_mock():
    with patch("cli.collaborator_commands.CollaboratorBL") as bl_cls:
        inst = MagicMock()
        bl_cls.return_value = inst
        yield inst


def test_update_success(runner, bl_mock):
    """Flot nominal: l’utilisateur saisit les trois nouveaux champs."""
    # collaborateur actuel
    bl_mock.get_by_id.return_value = SimpleNamespace(
        name="Jane", email="jane@corp.io", role_name="gestion"
    )
    # collaborateur après mise à jour
    bl_mock.update_collaborator.return_value = SimpleNamespace(
        name="Jane Doe", email="jane.doe@corp.io", role_name="support"
    )

    # Click.prompt est appelé 3× : nom, email, rôle
    with patch("cli.collaborator_commands.click.prompt",
               side_effect=["Jane Doe", "jane.doe@corp.io", "support"]):
        res = runner.invoke(cc.update_collaborator, ["1"])

    assert res.exit_code == 0
    assert "Collaborateur mis à jour : Jane Doe (jane.doe@corp.io) - rôle : support" in res.output
    bl_mock.update_collaborator.assert_called_once_with(
        1,
        {"name": "Jane Doe", "email": "jane.doe@corp.io", "role_name": "support"},
        {"id": 1, "role": "admin"},
    )


def test_collaborator_not_found(runner, bl_mock):
    """`get_by_id` lève une exception : message d'erreur affiché."""
    bl_mock.get_by_id.side_effect = Exception("introuvable")

    res = runner.invoke(cc.update_collaborator, ["99"])

    assert res.exit_code == 0
    assert "Erreur : introuvable" in res.output
    bl_mock.update_collaborator.assert_not_called()


def test_update_failure(runner, bl_mock):
    """Exception pendant `update_collaborator` : message d'erreur dédié."""
    # objet initial ok
    bl_mock.get_by_id.return_value = SimpleNamespace(
        name="John", email="john@corp.io", role_name="commercial"
    )
    bl_mock.update_collaborator.side_effect = Exception("conflit")

    with patch("cli.collaborator_commands.click.prompt",
               side_effect=["John Smith", "john.smith@corp.io", "gestion"]):
        res = runner.invoke(cc.update_collaborator, ["2"])

    assert res.exit_code == 0
    assert "Erreur lors de la mise à jour : conflit" in res.output