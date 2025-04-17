from click.testing import CliRunner
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

import cli.contract_commands as cc

# ---------------------------------------------------------------------------
# 1) Bypass decorator @with_auth_payload
# ---------------------------------------------------------------------------
_outer_cb = cc.show_contract_detail.callback
_inner_cb = _outer_cb.__wrapped__

def _bypass_auth(contract_id, *args, **kwargs):
    # injects a dummy current_user
    return _inner_cb(contract_id, current_user={"id": 1, "role": "admin"})

cc.show_contract_detail.callback = _bypass_auth


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


# Tests

def test_show_contract_detail_signed(runner, bl_mock):
    """
    Test the display of contract details for a signed contract.

    This function verifies that the contract details are correctly displayed
    when a contract is signed. It mocks the necessary backend logic to simulate
    retrieving contract information and validates the console output for
    accuracy and format.

    :param runner: The runner used to invoke the command-line interface.
    :type runner: Any
    :param bl_mock: The mocked backend logic for obtaining contract details.
    :type bl_mock: Any
    :return: None
    :rtype: None
    """
    c = SimpleNamespace(
        id=123,
        total_amount=1500.0,
        amount_left=0.0,
        status=True,
        client_id=42,
        commercial_id=7
    )
    bl_mock.get_contract.return_value = c

    res = runner.invoke(cc.show_contract_detail, ["123"])

    assert res.exit_code == 0
    output = res.output.splitlines()
    assert f"Contrat #123 :" in output[0]
    assert " - Montant total   : 1500.0" in output[1]
    assert " - Montant restant : 0.0" in output[2]
    assert " - Statut          : ✅ Signé" in output[3]
    assert "  - ID du client   : 42" in output[4]
    assert "  - ID du commercial : 7" in output[5]

def test_show_contract_detail_not_signed(runner, bl_mock):
    """
    Runs a test for showing the details of a contract that has not yet been signed.

    This function invokes the ``cc.show_contract_detail`` command with a contract ID,
    simulated using mocked data. The contract information is checked for proper display
    formats, ensuring the correct status and related fields are output. The specified
    contract is marked as not signed.

    The test verifies the following:
    - Correct exit code from the invoked command.
    - Proper formatting and content of the output, including the contract information
      and its signing status.

    :param runner: A test runner to execute CLI commands.
    :type runner: Any
    :param bl_mock: A mocked object for backend logic, providing contract data.
    :type bl_mock: Any
    :return: None
    """
    c = SimpleNamespace(
        id=456,
        total_amount=800.0,
        amount_left=200.0,
        status=False,
        client_id=99,
        commercial_id=15
    )
    bl_mock.get_contract.return_value = c

    res = runner.invoke(cc.show_contract_detail, ["456"])

    assert res.exit_code == 0
    lines = res.output.splitlines()
    assert lines[0].startswith("Contrat #456")
    assert " - Statut          : ❌ Non signé" in lines[3]

def test_show_contract_detail_not_found(runner, bl_mock):
    """
    Tests the behavior of the contract detail display functionality when the requested
    contract is not found. This ensures the system correctly handles the error raised
    by the backend logic and outputs an appropriate user-facing error message.

    :param runner: The test runner used to execute the CLI command.
    :param bl_mock: Mock object for business logic, used for simulating responses
        from the backend.
    :return: None
    """
    bl_mock.get_contract.side_effect = Exception("introuvable")

    res = runner.invoke(cc.show_contract_detail, ["999"])

    assert res.exit_code == 0
    assert "Erreur : introuvable" in res.output