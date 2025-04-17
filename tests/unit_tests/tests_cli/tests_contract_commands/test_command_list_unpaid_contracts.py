from click.testing import CliRunner
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

import cli.contract_commands as cc


# Bypass decorator @with_auth_payload

_outer_cb = cc.list_unpaid_contracts.callback
_inner_cb = _outer_cb.__wrapped__  # la vraie fonction métier

def _bypass_auth(*args, **kwargs):
    # Injects a dummy current_user and calls the internal function
    return _inner_cb(current_user={"id": 1, "role": "admin"})

cc.list_unpaid_contracts.callback = _bypass_auth  # patch définitif

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

def test_no_unpaid_contracts(runner, bl_mock):
    """
    Tests the functionality of the ``list_unpaid_contracts`` command when no unpaid
    contracts are present. Ensures that the command exits successfully and displays
    the appropriate message indicating that no unpaid contracts are found.

    :param runner: A test runner used to invoke the CLI command.
    :type runner: click.testing.CliRunner
    :param bl_mock: A mock object for business logic dependencies, allowing for
        controlled simulation of the program's state during testing.
    :return: None
    """
    bl_mock.list_unpaid_contract.return_value = []

    res = runner.invoke(cc.list_unpaid_contracts, [])

    assert res.exit_code == 0
    assert "Aucun contrat non payé trouvé." in res.output

def test_list_unpaid_contracts_success(runner, bl_mock):
    """
    Tests the successful listing of unpaid contracts by invoking the specified command.

    This function simulates the output of a command-line interface (CLI) command
    that retrieves unpaid contracts. It checks the proper integration of the
    functionality, ensures the correct format of the listed contracts, and validates
    the return exit code and output against expected results. It also mock-tests the
    business logic layer to avoid dependencies on external data or services.

    :param runner: The CLI runner object used to invoke the tested command.
    :type runner: CliRunner

    :param bl_mock: The mock object for the business logic (BL) layer which allows
        simulation and control of the behavior for the tests.
    :type bl_mock: Mock

    :return: None
    """
    c1 = SimpleNamespace(
        id=201,
        total_amount=1500,
        amount_left=500,
        client_id=30,
        creation_date="2025-03-15"
    )
    c2 = SimpleNamespace(
        id=202,
        total_amount=2000,
        amount_left=1000,
        client_id=31,
        creation_date="2025-04-10"
    )
    bl_mock.list_unpaid_contract.return_value = [c1, c2]

    res = runner.invoke(cc.list_unpaid_contracts, [])

    assert res.exit_code == 0
    assert "Contrats non payés :" in res.output

    line1 = f"- #{c1.id} | {c1.total_amount}€ / restant : {c1.amount_left}€ | Client : {c1.client_id} | Date de création : {c1.creation_date}"
    line2 = f"- #{c2.id} | {c2.total_amount}€ / restant : {c2.amount_left}€ | Client : {c2.client_id} | Date de création : {c2.creation_date}"
    assert line1 in res.output
    assert line2 in res.output

def test_error_during_unpaid_listing(runner, bl_mock):
    """
    Test the behavior of the command when an error occurs during the execution of
    listing unpaid contracts. This test ensures proper handling of exceptions raised
    by the `bl_mock.list_unpaid_contract`.

    :param runner: A test runner utility used to invoke CLI commands for testing.
    :type runner: Any
    :param bl_mock: A mock object for the business logic layer, simulating interactions
        and allowing for controlled exception generation.
    :type bl_mock: MagicMock
    :return: None
    """
    bl_mock.list_unpaid_contract.side_effect = Exception("Service indisponible")

    res = runner.invoke(cc.list_unpaid_contracts, [])

    assert res.exit_code == 0
    assert "Erreur : Service indisponible" in res.output