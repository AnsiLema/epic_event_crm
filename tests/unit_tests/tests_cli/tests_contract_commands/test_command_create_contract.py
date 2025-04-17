from click.testing import CliRunner
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest
from datetime import date

import cli.contract_commands as cc


# 1) Bypass du décorateur @with_auth_payload

_outer_cb = cc.create_contract.callback
_inner_cb = _outer_cb.__wrapped__

def _bypass_auth(*args, **kwargs):
    # injecte un current_user factice
    kwargs["current_user"] = {"id": 1, "role": "admin"}
    return _inner_cb(*args, **kwargs)

cc.create_contract.callback = _bypass_auth  # patch définitif


# Fixtures

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

# 3) Tests

def test_create_contract_with_options(runner, bl_mock):
    """
    Tests the creation of a contract with given options using the `runner` and a mocked
    business logic (`bl_mock`). Validates the behavior of the `create_contract` function,
    ensuring that the input arguments are passed correctly, the expected output is
    produced, and the mock is called with accurate data.

    :param runner: A test runner object responsible for invoking the command-line
        interface command `create_contract`.
    :param bl_mock: A mocked object providing a mock implementation for the
        `create_contract` method in the underlying business logic.
    :return: None
    """
    bl_mock.create_contract.return_value = SimpleNamespace(
        id=10, total_amount=100.0
    )

    result = runner.invoke(
        cc.create_contract,
        [
            "--client-id", "42",
            "--commercial-id", "7",
            "--total-amount", "100.0",
            "--amount-left", "25.0",
        ],
    )

    assert result.exit_code == 0
    assert "Contrat créé : #10 -  Montant : 100.0€, Statut : Non Signé" in result.output

    bl_mock.create_contract.assert_called_once()
    data_arg, user_arg = bl_mock.create_contract.call_args[0]

    assert data_arg["client_id"] == 42
    assert data_arg["commercial_id"] == 7
    assert data_arg["total_amount"] == 100.0
    assert data_arg["amount_left"] == 25.0

    assert isinstance(data_arg["creation_date"], date)
    assert data_arg["creation_date"] == date.today()
    assert data_arg["status"] is False

    assert user_arg == {"id": 1, "role": "admin"}

def test_create_contract_via_prompts(runner, bl_mock):
    """
    Tests the creation of a contract using user prompts. The function simulates user
    input and validates the contract creation process through the mocked business
    logic layer.

    This test ensures that the user is prompted for contract data (client ID,
    commercial ID, total amount, and amount left), processes the inputs correctly,
    and validates the output message as well as invocation of the mocked method.

    :param runner: The test runner utility object used to invoke the CLI commands.
    :type runner: Any
    :param bl_mock: The mock object for the business logic which includes methods
                    for contract creation.
    :type bl_mock: unittest.mock.Mock
    :return: None
    """
    bl_mock.create_contract.return_value = SimpleNamespace(
        id=20, total_amount=200.0
    )

    # Data client-id, commercial-id, total_amount, amount_left
    user_input = "\n".join(["55", "8", "200.0", "50.0"]) + "\n"

    result = runner.invoke(cc.create_contract, input=user_input)

    assert result.exit_code == 0
    assert "Contrat créé : #20 -  Montant : 200.0€, Statut : Non Signé" in result.output
    bl_mock.create_contract.assert_called_once()

@pytest.mark.parametrize("exc,msg", [
    (ValueError("Données invalides"), "Données invalides"),
    (Exception("Erreur BDD"), "Erreur BDD"),
])
def test_create_contract_error(runner, bl_mock, exc, msg):
    """
    Tests the behavior of the `create_contract` command when an exception occurs
    during the business logic operation. The test ensures error messages are
    properly displayed and that the business logic's method is invoked exactly
    once with the provided parameters.

    :param runner: A test runner instance used to invoke commands in the CLI.
    :param bl_mock: A mock object simulating the behavior of the business logic.
    :param exc: The exception to be raised by the `create_contract` method during the test.
    :param msg: The expected error message corresponding to the raised exception.
    :return: None
    """
    bl_mock.create_contract.side_effect = exc

    result = runner.invoke(
        cc.create_contract,
        [
            "--client-id", "1",
            "--commercial-id", "2",
            "--total-amount", "10.0",
            "--amount-left", "5.0",
        ],
    )

    assert result.exit_code == 0
    assert f"Erreur : {msg}" in result.output
    bl_mock.create_contract.assert_called_once()