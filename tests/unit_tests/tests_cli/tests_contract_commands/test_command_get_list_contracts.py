from click.testing import CliRunner
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

import cli.contract_commands as cc


# Bypass decorator @with_auth_payload
outer_cb = cc.list_contracts.callback
inner_cb = outer_cb.__wrapped__

def bypass_auth(full, *args, **kwargs):
    # Injects a dummy current_user and calls the internal function
    return inner_cb(full, current_user={"id": 1, "role": "admin"})

cc.list_contracts.callback = bypass_auth


@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def patch_session():
    """
    Fixture that automatically patches the `Session` class used in the `cli.contract_commands`
    module with a mock object. This allows isolation of test code from external dependencies
    and ensures that the tests do not rely on the actual implementation of the `Session` class.

    The patched `Session` class is replaced by a mocked object created with `MagicMock`.

    :return: A mock object representing the patched `Session` class.
    :rtype: unittest.mock.MagicMock
    """
    with patch("cli.contract_commands.Session") as sess_cls:
        sess_cls.return_value = MagicMock()
        yield sess_cls

@pytest.fixture
def bl_mock():
    """
    Creates a pytest fixture for mocking the `ContractBL` class.

    The function uses the unittest.mock.patch utility to temporarily replace the
    `ContractBL` class with a mock during the execution of the test where the
    fixture is used. By yielding the mock instance of the `ContractBL` class,
    test authors can control its behavior as needed for the test context.

    :yield: Yields a MagicMock instance that represents the mocked `ContractBL`
        class, allowing the test to customize behavior and assertions.
    """
    with patch("cli.contract_commands.ContractBL") as bl_cls:
        inst = MagicMock()
        bl_cls.return_value = inst
        yield inst


def test_no_contracts_found(runner, bl_mock):
    """
    Tests the behavior of the application when no contracts are found.

    This function mocks the behavior of listing all contracts to simulate
    a scenario where no contracts are available. It invokes the command to
    list contracts and verifies the correct exit code and output message
    indicating no contracts were found.

    :param runner: The test runner provided by the testing framework.
    :param bl_mock: A mock object used to replace the business logic layer
                    for retrieving contracts.
    :return: None
    """
    bl_mock.list_all_contracts.return_value = []

    res = runner.invoke(cc.list_contracts, [])

    assert res.exit_code == 0
    assert "Aucun contrat trouvé." in res.output

def test_list_basic_details(runner, bl_mock):
    """
    Tests the basic listing of contract details using the `list_contracts` command.
    This test validates that all contracts are displayed with correct information
    and ensures that no extended details (e.g., client or commercial IDs) are included
    in the output.

    :param runner: A click runner object used for invoking CLI commands.
    :type runner: CliRunner
    :param bl_mock: A mock object representing the business logic layer, used to
        simulate the list of contracts returned by the backend.
    :type bl_mock: MagicMock
    :return: None
    """
    c1 = SimpleNamespace(id=1, status=True, total_amount=1000, amount_left=0,
                         client_id=10, commercial_id=20)
    c2 = SimpleNamespace(id=2, status=False, total_amount=500, amount_left=200,
                         client_id=11, commercial_id=21)
    bl_mock.list_all_contracts.return_value = [c1, c2]

    res = runner.invoke(cc.list_contracts, [])

    assert res.exit_code == 0
    expected1 = f"Contrat #{c1.id} | ✅ Signé | Montant : {c1.total_amount}€ / restant : {c1.amount_left}€"
    expected2 = f"Contrat #{c2.id} | ❌ Non signé | Montant : {c2.total_amount}€ / restant : {c2.amount_left}€"
    assert expected1 in res.output
    assert expected2 in res.output
    # Pas de détails étendus
    assert "ID du client" not in res.output
    assert "Id du commercial" not in res.output

def test_list_with_full_flag(runner, bl_mock):
    """
    Tests the listing of contracts with the `--full` flag.

    This function uses a mocked business logic layer to simulate contract data
    and checks whether the output contains the expected detailed information about
    the contracts, based on the `--full` option.

    :param runner: The test runner used to simulate CLI commands.
    :type runner: Any
    :param bl_mock: A mock object for the business logic layer.
    :type bl_mock: unittest.mock.Mock
    :return: None
    :rtype: None
    """
    c = SimpleNamespace(id=3, status=False, total_amount=750, amount_left=100,
                        client_id=42, commercial_id=99)
    bl_mock.list_all_contracts.return_value = [c]

    res = runner.invoke(cc.list_contracts, ["--full"])

    assert res.exit_code == 0
    base = f"Contrat #{c.id} | ❌ Non signé | Montant : {c.total_amount}€ / restant : {c.amount_left}€"
    full_line = f"{base} | ID du client : {c.client_id} | Id du commercial : {c.commercial_id}"
    # Vérifie la chaîne complète
    assert full_line in res.output

def test_error_during_list(runner, bl_mock):
    """
    Tests handling of an error occurring during contract listing when interacting
    with the database. Simulates an exception thrown due to database unavailability
    and verifies that the output reflects the error appropriately.

    :param runner: CLI test runner, used to invoke commands and capture output
    :type runner: click.testing.CliRunner
    :param bl_mock: Mock of the business logic layer, used to simulate behaviors
    :type bl_mock: unittest.mock.Mock
    :return: None
    """
    bl_mock.list_all_contracts.side_effect = Exception("DB down")

    res = runner.invoke(cc.list_contracts, [])

    assert res.exit_code == 0
    assert "Erreur : DB down" in res.output