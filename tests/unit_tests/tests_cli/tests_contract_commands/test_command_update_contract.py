from click.testing import CliRunner
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

import cli.contract_commands as cc


# Bypass du décorateur @with_auth_payload

_outer_cb = cc.update_contract.callback
_inner_cb = _outer_cb.__wrapped__  # la vraie fonction métier

def _bypass_auth(contract_id, *args, **kwargs):
    # injects a dummy current_user
    return _inner_cb(contract_id, current_user={"id": 1, "role": "admin"})

cc.update_contract.callback = _bypass_auth

# Fixtures communes

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def patch_session():
    with patch("cli.contract_commands.Session") as sess_cls:
        sess_cls.return_value = MagicMock()
        yield sess_cls

@pytest.fixture
def bl_mock():
    with patch("cli.contract_commands.ContractBL") as bl_cls:
        inst = MagicMock()
        bl_cls.return_value = inst
        yield inst

# Tests

def test_update_contract_success(runner, bl_mock):
    """
    Tests the successful execution of the `update_contract` command.

    This function verifies that a contract can be updated using user input
    prompted via the CLI. It includes checks to ensure the proper display of
    the current contract state, correct modification of the contract attributes,
    and invocation of the associated interface methods with the expected parameters.

    :param runner: The testing interface to invoke CLI commands.
    :type runner: CliRunner
    :param bl_mock: Mock object to simulate the contract business logic interface.
    :type bl_mock: unittest.mock.Mock
    :return: None
    """

    orig = SimpleNamespace(id=5, total_amount=100.0, amount_left=40.0, status=False)
    bl_mock.get_contract.return_value = orig

    updated = SimpleNamespace(id=5, total_amount=120.0, amount_left=0.0, status=True)
    bl_mock.update_contract.return_value = updated

    with patch("cli.contract_commands.click.prompt", side_effect=[120.0, 0.0]), \
         patch("cli.contract_commands.click.confirm", return_value=True):
        res = runner.invoke(cc.update_contract, ["5"])

    assert res.exit_code == 0
    assert "Contrat Actuel : #5" in res.output
    assert "Contrat mis à jour : #5 | Total : 120.0€, Statut : ✅ Signé" in res.output
    bl_mock.update_contract.assert_called_once_with(
        5,
        {"total_amount": 120.0, "amount_left": 0.0, "status": True},
        {"id": 1, "role": "admin"}
    )

def test_update_contract_not_found(runner, bl_mock):
    """
    Tests the behavior of the `update_contract` command when the specified contract
    is not found. This function mocks the behavior of a backend service to simulate
    a contract retrieval failure and verifies the output and behavior of the
    command under test.

    :param runner: Click test runner used to invoke CLI commands.
    :type runner: click.testing.CliRunner
    :param bl_mock: Mock object for the backend logic layer, which simulates
        contract retrieval and update functionality.
    :type bl_mock: unittest.mock.Mock
    :return: None
    """
    bl_mock.get_contract.side_effect = Exception("introuvable")

    res = runner.invoke(cc.update_contract, ["99"])

    assert res.exit_code == 0
    assert "Erreur : introuvable" in res.output
    bl_mock.update_contract.assert_not_called()

def test_update_contract_error_during_update(runner, bl_mock):
    """
    This test simulates the update of an existing contract where an error occurs during
    the update process in the backend. The test verifies that the error is correctly
    handled and that the appropriate error message is returned to the end user.

    :param runner: Test runner instance to invoke the CLI command under test.
    :type runner: CliRunner
    :param bl_mock: Mock object for the business logic layer used to simulate
        interactions with contract management functions.
    :type bl_mock: unittest.mock.Mock
    :return: None
    """
    # arrange: contrat existant
    orig = SimpleNamespace(id=7, total_amount=200.0, amount_left=50.0, status=True)
    bl_mock.get_contract.return_value = orig
    # arrange: erreur en update
    bl_mock.update_contract.side_effect = Exception("pb SQL")

    with patch("cli.contract_commands.click.prompt", side_effect=[210.0, 40.0]), \
         patch("cli.contract_commands.click.confirm", return_value=False):
        # Note: confirm=False → code prints "Contrat mis à jour" only if confirm true
        # But here confirm False bypasses update branch entirely; so to test exception,
        # force confirm=True:
        pass

    # to test exception during update, forced confirm=True
    with patch("cli.contract_commands.click.prompt", side_effect=[210.0, 40.0]), \
         patch("cli.contract_commands.click.confirm", return_value=True):
        res = runner.invoke(cc.update_contract, ["7"])

    assert res.exit_code == 0
    assert "Erreur pendant la mis à jour: pb SQL" in res.output
    bl_mock.update_contract.assert_called_once_with(
        7,
        {"total_amount": 210.0, "amount_left": 40.0, "status": True},
        {"id": 1, "role": "admin"}
    )