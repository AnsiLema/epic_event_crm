# tests/unit_tests/tests_cli/tests_collaborator_commands/test_delete_collaborator_command.py
from click.testing import CliRunner
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

import cli.collaborator_commands as cc


_outer_cb = cc.delete_collaborator.callback
_inner_cb = _outer_cb.__wrapped__  # la vraie fonction métier

def _bypass_auth(collaborator_id, *args, **kwargs):
    # injecte current_user factice
    return _inner_cb(collaborator_id, current_user={"id": 1, "role": "admin"})

cc.delete_collaborator.callback = _bypass_auth

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def patch_session():
    with patch("cli.collaborator_commands.Session") as sess_cls:
        sess_cls.return_value = MagicMock()
        yield sess_cls

@pytest.fixture
def bl_mock():
    with patch("cli.collaborator_commands.CollaboratorBL") as bl_cls:
        instance = MagicMock()
        bl_cls.return_value = instance
        yield instance

# --------------------------------------------------------------------------
# 3) Tests
# --------------------------------------------------------------------------
def test_delete_success_confirm_yes(runner, bl_mock):
    """
    Tests the successful deletion of a collaborator when the confirmation prompt receives
    a positive response.

    This test case verifies that the `delete_collaborator` function behaves correctly when
    the user confirms the deletion of a collaborator. It mocks the `get_by_id` and
    `delete_collaborator` methods to simulate the retrieval and deletion of a specific
    collaborator. Additionally, it patches the `click.confirm` method to ensure a simulated
    positive response for confirmation.

    :param runner: The CLI test runner used to invoke the command.
    :type runner: pytest fixture or equivalent for CLI testing
    :param bl_mock: The mock object for the business logic layer, used to mock collaborator
        retrieval and deletion methods.
    :type bl_mock: unittest.mock.Mock
    :return: None
    """
    bl_mock.get_by_id.return_value = SimpleNamespace(
        name="Alice", email="alice@corp.io", role_name="support"
    )
    bl_mock.delete_collaborator.return_value = None

    with patch("cli.collaborator_commands.click.confirm", return_value=True):
        res = runner.invoke(cc.delete_collaborator, ["42"])

    assert res.exit_code == 0
    assert "⚠️ Vous êtes sur le point de supprimer : Alice (alice@corp.io) - rôle : support" in res.output
    assert "Collaborateur supprimé avec succès." in res.output
    bl_mock.delete_collaborator.assert_called_once_with(42, {"id": 1, "role": "admin"})

def test_delete_cancelled_confirm_no(runner, bl_mock):
    """
    Tests that the deletion operation is cancelled when the user confirms "no". It
    simulates the behavior of the `delete_collaborator` command with a mocked
    `bl_mock` service and a simulated user response through `click.confirm`. The
    function ensures that no collaborator deletion action is taken when the user
    rejects the confirmation prompt.

    :param runner: CLI test runner instance used to invoke commands.
    :type runner: click.testing.CliRunner
    :param bl_mock: Mock object for the business logic layer handling collaborators.
    :type bl_mock: unittest.mock.Mock
    :return: None
    """
    bl_mock.get_by_id.return_value = SimpleNamespace(
        name="Bob", email="bob@corp.io", role_name="gestion"
    )

    with patch("cli.collaborator_commands.click.confirm", return_value=False):
        res = runner.invoke(cc.delete_collaborator, ["7"])

    assert res.exit_code == 0
    assert "Suppression annulée." in res.output
    bl_mock.delete_collaborator.assert_not_called()

def test_delete_not_found(runner, bl_mock):
    """
    Tests the behavior of the `delete_collaborator` command when attempting
    to delete a non-existent collaborator. The test ensures that the appropriate
    error message is displayed, no delete operation is performed, and the
    command exits gracefully with a success exit code.

    :param runner: A test runner instance used to invoke CLI commands.
    :param bl_mock: A mock object representing the business logic layer,
        allowing for simulation of method calls and error handling.
    :return: None
    """
    bl_mock.get_by_id.side_effect = Exception("introuvable")

    res = runner.invoke(cc.delete_collaborator, ["99"])

    assert res.exit_code == 0
    assert "Erreur : introuvable" in res.output
    bl_mock.delete_collaborator.assert_not_called()

def test_delete_error_on_delete(runner, bl_mock):
    """
    Tests the behavior of the `delete_collaborator` command when an error occurs
    during the deletion process. Verifies if an error message is displayed
    and the collaborator deletion method is called appropriately.

    :param runner: Fixture providing a test client for invoking CLI commands.
    :param bl_mock: Mock of the business logic layer to simulate the
        behavior of `get_by_id` and `delete_collaborator` methods.
    :return: None
    """
    bl_mock.get_by_id.return_value = SimpleNamespace(
        name="Carol", email="carol@corp.io", role_name="commercial"
    )
    bl_mock.delete_collaborator.side_effect = Exception("erreur SQL")

    with patch("cli.collaborator_commands.click.confirm", return_value=True):
        res = runner.invoke(cc.delete_collaborator, ["15"])

    assert res.exit_code == 0
    assert "Erreur lors de la suppression : erreur SQL" in res.output
    bl_mock.delete_collaborator.assert_called_once_with(15, {"id": 1, "role": "admin"})