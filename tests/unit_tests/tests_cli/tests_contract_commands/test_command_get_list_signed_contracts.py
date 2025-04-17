from click.testing import CliRunner
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

import cli.contract_commands as cc

# ---------------------------------------------------------------------------
# Bypass decorator @with_auth_payload

_outer_cb = cc.list_signed_contracts.callback
_inner_cb = _outer_cb.__wrapped__  # la vraie fonction métier

def _bypass_auth(*args, **kwargs):
    # Injects a dummy current_user and calls the internal function
    return _inner_cb(current_user={"id": 1, "role": "admin"})

cc.list_signed_contracts.callback = _bypass_auth  # patch définitif

# Fixtures

@pytest.fixture
def runner() -> CliRunner:
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

def test_no_signed_contracts(runner, bl_mock):
    """
    Tests the behavior of the `list_signed_contracts` command when there are no signed contracts.

    The function ensures the correct output is displayed when the `list_signed_contracts`
    response is an empty list. It simulates the behavior of the `bl_mock` mock object to
    return no signed contracts and verifies that the appropriate message is included
    in the command output and the command exits successfully.

    :param runner: The command line interface runner used to invoke the command.
    :type runner: click.testing.CliRunner
    :param bl_mock: A mock object for the business logic layer, used to mock the
        behavior of the `list_signed_contracts` method.
    :type bl_mock: unittest.mock.Mock
    :return: None
    """
    bl_mock.list_signed_contracts.return_value = []

    res = runner.invoke(cc.list_signed_contracts, [])

    assert res.exit_code == 0
    assert "Aucun contrat signé trouvé." in res.output

def test_list_signed_contracts_success(runner, bl_mock):
    """
    Test function for verifying the successful listing of signed contracts. Ensures the command outputs
    the expected details including contract ID, total amount, amount left, client ID, and creation date.

    :param runner: The test CLI runner for invoking command-line commands within tests.
    :type runner: Any
    :param bl_mock: The mock object representing the business logic layer, used to define return values
                    or expected interactions.
    :type bl_mock: unittest.mock.Mock
    :return: None
    :rtype: None
    """
    c1 = SimpleNamespace(
        id=101,
        total_amount=1200,
        amount_left=0,
        client_id=55,
        creation_date="2025-04-01"
    )
    c2 = SimpleNamespace(
        id=102,
        total_amount=800,
        amount_left=200,
        client_id=56,
        creation_date="2025-04-02"
    )
    bl_mock.list_signed_contracts.return_value = [c1, c2]

    res = runner.invoke(cc.list_signed_contracts, [])

    assert res.exit_code == 0
    assert "Contrats signés :" in res.output
    line1 = f"- #{c1.id} | {c1.total_amount}€ / {c1.amount_left} | Client : {c1.client_id} | Date de création : {c1.creation_date}"
    assert line1 in res.output
    line2 = f"- #{c2.id} | {c2.total_amount}€ / {c2.amount_left} | Client : {c2.client_id} | Date de création : {c2.creation_date}"
    assert line2 in res.output

def test_error_during_listing(runner, bl_mock):
    """
    Tests the behavior of the application when an error occurs during the listing
    of signed contracts. Specifically, simulates a database access error and
    verifies the program's response.

    :param runner: Command-line test runner used to invoke the application commands.
    :type runner: object
    :param bl_mock: Mocked business logic object used to simulate the
        behavior of the list_signed_contracts function.
    :type bl_mock: object
    :return: None
    """
    bl_mock.list_signed_contracts.side_effect = Exception("DB inaccessible")

    res = runner.invoke(cc.list_signed_contracts, [])

    assert res.exit_code == 0
    assert "Erreur : DB inaccessible" in res.output