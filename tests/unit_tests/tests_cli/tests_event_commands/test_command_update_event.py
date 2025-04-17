# tests/unit_tests/tests_cli/tests_event_commands/test_update_event_command.py
from click.testing import CliRunner
from types import SimpleNamespace
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest

import cli.event_commands as cc


# Bypass du décorateur @with_auth_payload

_original_cb = cc.update_event.callback
_inner_fn    = _original_cb.__wrapped__

def _bypass_auth(event_id, *args, **kwargs):
    # simulate a support user by default; tests can override current_user.role
    return _inner_fn(event_id, current_user={"id": 1, "role": kwargs.get("role", "support")})

cc.update_event.callback = _bypass_auth


# Fixtures

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def patch_session():
    with patch("cli.event_commands.Session") as sess_cls:
        sess_cls.return_value = MagicMock()
        yield sess_cls

@pytest.fixture
def bl_mock():
    with patch("cli.event_commands.EventBL") as bl_cls:
        inst = MagicMock()
        bl_cls.return_value = inst
        yield inst

# Tests

def test_get_event_error(runner, bl_mock):
    """
    Tests the behavior of the `update_event` command when an exception is raised
    while attempting to fetch the event. This ensures the application correctly
    handles the error, providing proper output and avoiding further execution
    like `update_event`.

    :param runner: Test runner used to invoke the command.
    :type runner: Runner
    :param bl_mock: Mock object for business logic layer used to simulate
        event retrieval and update behavior.
    :type bl_mock: Mock
    :return: None
    """
    bl_mock.get_event.side_effect = Exception("not found")

    res = runner.invoke(cc.update_event, ["10"])

    assert res.exit_code == 0
    assert "Erreur : not found" in res.output
    bl_mock.get_event.assert_called_once_with(10)
    bl_mock.update_event.assert_not_called()

def test_support_modify_some_fields(runner, bl_mock):
    """
    Tests the functionality to modify specific fields of an event via a command-line interface
    interaction. The test mocks user inputs for confirmation and prompts to verify that only
    the intended fields are updated, and others remain unchanged.

    :param runner: The test runner that simulates invoking CLI commands
    :type runner: click.testing.CliRunner
    :param bl_mock: A mock object representing the business logic layer
    :type bl_mock: unittest.mock.MagicMock
    :return: None
    """
    original_event = SimpleNamespace(
        id=20,
        contract_id=5,
        start_date=datetime(2025, 4, 17, 9, 0),
        end_date=datetime(2025, 4, 17, 17, 0),
        location="OldLoc",
        attendees=10,
        note="OK",
        support_id=2
    )
    bl_mock.get_event.return_value = original_event
    bl_mock.update_event.return_value = SimpleNamespace(id=20)

    confirm_side_effects = [True, False, True, False, False]
    prompt_side_effects = [
        "2025-04-18 08:30",
        "NewLoc"
    ]

    with patch("cli.event_commands.click.confirm", side_effect=confirm_side_effects), \
         patch("cli.event_commands.click.prompt", side_effect=prompt_side_effects):
        result = runner.invoke(cc.update_event, ["20"])

    assert result.exit_code == 0

    # Checks the call to update_event
    bl_mock.update_event.assert_called_once()
    called_args = bl_mock.update_event.call_args[0]
    assert called_args[0] == 20  # contract_id

    updates_dict = called_args[1]
    # Only start_date and location must be present
    assert updates_dict["start_date"] == datetime(2025, 4, 18, 8, 30)
    assert updates_dict["location"] == "NewLoc"
    for key in ("end_date", "attendees", "note"):
        assert key not in updates_dict

    current_user_arg = called_args[2]
    assert current_user_arg == {"id": 1, "role": "support"}

def test_support_no_modification(runner, bl_mock):
    """
    Tests the behavior of the `update_event` command when no modifications are
    selected, ensuring that no updates are made to the event and appropriate
    messages are displayed.

    :param runner: The CLI test runner used to invoke the command.
    :type runner: CliRunner
    :param bl_mock: A mock object for the business logic layer, providing
        functionality such as retrieving and updating events.
    :type bl_mock: Mock
    :return: None
    """
    evt = SimpleNamespace(
        id=21, contract_id=6,
        start_date=datetime.now(),
        end_date=datetime.now(),
        location="L",
        attendees=1, note=None, support_id=None
    )
    bl_mock.get_event.return_value = evt

    # all confirms false
    with patch("cli.event_commands.click.confirm", return_value=False):
        res = runner.invoke(cc.update_event, ["21"])

    assert res.exit_code == 0
    assert "Aucune modification sélectionnée" in res.output
    bl_mock.update_event.assert_not_called()

def test_management_modify_support(runner, bl_mock):
    """
    Tests the functionality of updating the support_id of an event while ensuring
    the 'management' user role is enforced. This test mockingly simulates the
    behavior of invoking a CLI command for event updates and verifies that only
    the support_id attribute is updated, while ensuring proper role validation.

    :param runner: The test runner object used to invoke CLI commands.
    :param bl_mock: The mocked business logic layer object to simulate database
        operations and other interactions.
    :return: None
    """
    evt = SimpleNamespace(
        id=30,
        contract_id=7,
        start_date=datetime.now(),
        end_date=datetime.now(),
        location="X",
        attendees=2,
        note="",
        support_id=3
    )
    bl_mock.get_event.return_value = evt
    bl_mock.update_event.return_value = SimpleNamespace(id=30)

    # We replace the callback to force the 'management' role
    def bypass_mgmt(event_id, *args, **kwargs):
        return _inner_fn(event_id, current_user={"id": 1, "role": "management"})
    cc.update_event.callback = bypass_mgmt

    # Act: confirm the modification of the support, then enter "5"
    with patch("cli.event_commands.click.confirm", side_effect=[True]), \
         patch("cli.event_commands.click.prompt", return_value="5"):
        result = runner.invoke(cc.update_event, ["30"])

    # Assert
    assert result.exit_code == 0

    args, _ = bl_mock.update_event.call_args
    assert args[0] == 30
    updates = args[1]
    assert updates == {"support_id": 5}
    user_arg = args[2]
    assert user_arg["role"] == "management"

def test_management_no_modification(runner, bl_mock):
    """
    Tests the behavior of the `update_event` CLI command when no modifications are
    selected by the user. The test ensures that the command does not proceed with
    updating an event if no changes are confirmed explicitly and validates that no
    calls are made to the backend for updating the event.

    :param runner: pytest fixture that allows invoking CLI commands for testing.
    :type runner: Runner
    :param bl_mock: Mock object representing the business logic layer used to interact
        with event data.
    :type bl_mock: Mock
    :return: None
    """
    evt = SimpleNamespace(
        id=31, contract_id=8,
        start_date=datetime.now(),
        end_date=datetime.now(),
        location="Y",
        attendees=3, note="", support_id=None
    )
    bl_mock.get_event.return_value = evt

    def bypass_mgmt(event_id, *args, **kwargs):
        return _inner_fn(event_id, current_user={"id": 1, "role": "management"})
    cc.update_event.callback = bypass_mgmt

    with patch("cli.event_commands.click.confirm", return_value=False):
        res = runner.invoke(cc.update_event, ["31"])

    assert res.exit_code == 0
    assert "Aucune modification sélectionnée" in res.output
    bl_mock.update_event.assert_not_called()

def test_unauthorized_user(runner, bl_mock):
    """
    Test the access control for unauthorized users when attempting to update an event via the CLI command.

    This function verifies that a user without sufficient privileges, such as having a "guest"
    role, cannot update an event. It simulates an attempt to execute the `update_event`
    command with a certain user role and ensures that the desired restrictions are enforced.

    :param runner: CLI test runner used to invoke commands.
    :type runner: click.testing.CliRunner
    :param bl_mock: Mock object to simulate the behavior of business logic or service layer.
    :type bl_mock: unittest.mock.Mock
    :return: None
    """
    evt = SimpleNamespace(
        id=40, contract_id=9,
        start_date=datetime.now(),
        end_date=datetime.now(),
        location="Z",
        attendees=4, note="", support_id=None
    )
    bl_mock.get_event.return_value = evt
    # override role to e.g. "guest"
    def bypass_guest(event_id, *args, **kwargs):
        return _inner_fn(event_id, current_user={"id": 1, "role": "guest"})
    cc.update_event.callback = bypass_guest

    res = runner.invoke(cc.update_event, ["40"])

    assert res.exit_code == 0
    assert "Vous n'avez pas les droits" in res.output
    bl_mock.update_event.assert_not_called()