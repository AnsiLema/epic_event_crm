from click.testing import CliRunner
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

import cli.contract_commands as cc


# Bypass decorator @with_auth_payload

outer_cb = cc.list_unsigned_contracts.callback
inner_cb = outer_cb.__wrapped__  # la vraie fonction métier

def bypass_auth(*args, **kwargs):
    # Injects a dummy current_user and calls the internal function
    return inner_cb(current_user={"id": 1, "role": "admin"})

cc.list_unsigned_contracts.callback = bypass_auth

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

def test_no_unsigned_contracts(runner, bl_mock):
    """
    Tests the scenario where there are no unsigned contracts.

    This test verifies the behavior of the `list_unsigned_contracts` functionality
    when no unsigned contracts are present in the system. It checks if the command
    outputs the correct message and exits with a success status.

    :param runner: The CLI test runner used for invoking commands.
    :type runner: Any
    :param bl_mock: Mock object for business logic layer, used to simulate
        dependencies.
    :type bl_mock: unittest.mock.Mock
    :return: None
    """
    bl_mock.list_unsigned_contracts.return_value = []

    res = runner.invoke(cc.list_unsigned_contracts, [])

    assert res.exit_code == 0
    assert "Aucun contrat non signé trouvé." in res.output

def test_list_unsigned_contracts_success(runner, bl_mock):
    """
    Tests the successful listing of unsigned contracts using the provided runner and mocked
    business logic (bl_mock). This includes asserting the command execution, output format,
    and completeness of the contract information in the result.

    :param runner: The command runner instance used to invoke the contract listing command.
    :type runner: Runner
    :param bl_mock: Mock object for abstraction layer handling contracts, used to simulate
        the contracts fetching logic. It must provide a `list_unsigned_contracts`
        method returning a list of SimpleNamespace objects representing unsigned contracts.
    :type bl_mock: Mock
    :return: None
    """
    c1 = SimpleNamespace(
        id=301,
        total_amount=900,
        amount_left=900,
        client_id=70,
        creation_date="2025-04-05"
    )
    c2 = SimpleNamespace(
        id=302,
        total_amount=400,
        amount_left=150,
        client_id=71,
        creation_date="2025-04-06"
    )
    bl_mock.list_unsigned_contracts.return_value = [c1, c2]

    res = runner.invoke(cc.list_unsigned_contracts, [])

    assert res.exit_code == 0
    assert "Contrat non signé" in res.output

    line1 = f"- #{c1.id} | {c1.total_amount}€ / Restant : {c1.amount_left} | Client : {c1.client_id} | Date de création : {c1.creation_date}"
    line2 = f"- #{c2.id} | {c2.total_amount}€ / Restant : {c2.amount_left} | Client : {c2.client_id} | Date de création : {c2.creation_date}"
    assert line1 in res.output
    assert line2 in res.output

def test_error_during_unsigned_listing(runner, bl_mock):
    """
    Tests the behavior of the system when an error occurs during the listing
    of unsigned contracts. Ensures that the relevant error message is
    displayed and the command completes with the correct exit code.

    :param runner: Test runner used to invoke command-line interfaces
    :param bl_mock: Mock object for business logic, used to simulate the
        behavior of the listing service
    :return: None
    """
    bl_mock.list_unsigned_contracts.side_effect = Exception("Service down")

    res = runner.invoke(cc.list_unsigned_contracts, [])

    assert res.exit_code == 0
    assert "Erreur : Service down" in res.output