import pytest
from click.testing import CliRunner
from types import SimpleNamespace
from datetime import datetime
from unittest.mock import MagicMock, patch

import cli.event_commands as cc


# Bypass decorator @with_auth_payload
_outer_cb = cc.list_events_without_support.callback
_inner_fn = _outer_cb.__wrapped__

def _bypass_auth(*args, **kwargs):
    # injecte un current_user factice
    return _inner_fn(current_user={"id": 1, "role": "admin"})

cc.list_events_without_support.callback = _bypass_auth

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
def test_no_events_without_support(runner, bl_mock):
    """
    Test the `list_events_without_support` command under a scenario where no events exist that
    lack support. Ensures proper feedback is returned to the user indicating no such events
    exist.

    :param runner: A test runner instance that simulates invoking the `list_events_without_support`
        command within the CLI context.
    :param bl_mock: A mock instance of the business logic layer, injected to simulate backend behavior
        in the absence of actual data or process execution.
    :return: None
    """
    bl_mock.list_events_without_support.return_value = []

    result = runner.invoke(cc.list_events_without_support, [])

    assert result.exit_code == 0
    assert "Tous les événements ont un support assigné." in result.output

def test_list_events_without_support_success(runner, bl_mock):
    """
    Tests the functionality of listing events that do not yet have support. This function
    simulates a scenario where a command-line runner is utilized to invoke the command
    for listing events without support. It validates that the command runs successfully
    and produces the expected output format, comparing the actual output to the expected
    representation of event data.

    :param runner: The command-line runner used to invoke the command.
    :type runner: Click.testing.CliRunner
    :param bl_mock: A mock object representing the business logic layer, which is used
        to simulate returned data for events.
    :type bl_mock: unittest.mock.Mock
    :return: None
    """
    e1 = SimpleNamespace(
        id=101,
        start_date=datetime(2025, 5, 1, 9, 0),
        end_date=datetime(2025, 5, 1, 11, 0),
        location="Salle A"
    )
    e2 = SimpleNamespace(
        id=102,
        start_date=datetime(2025, 5, 2, 14, 30),
        end_date=datetime(2025, 5, 2, 16, 0),
        location="Salle B"
    )
    bl_mock.list_events_without_support.return_value = [e1, e2]

    result = runner.invoke(cc.list_events_without_support, [])

    assert result.exit_code == 0
    # En-tête
    assert "Événements sans support :" in result.output
    # Détails ligne 1
    line1 = (
        f"- ID #{e1.id} | Début : {e1.start_date.strftime('%Y-%m-%d %H:%M')} "
        f"| {e1.end_date.strftime('%Y-%m-%d %H:%M')} | Lieu : {e1.location}"
    )
    assert line1 in result.output
    # Détails ligne 2
    line2 = (
        f"- ID #{e2.id} | Début : {e2.start_date.strftime('%Y-%m-%d %H:%M')} "
        f"| {e2.end_date.strftime('%Y-%m-%d %H:%M')} | Lieu : {e2.location}"
    )
    assert line2 in result.output

def test_permission_error(runner, bl_mock):
    """
    Tests the behavior of the function when a permission error occurs while trying
    to execute 'list_events_without_support'. The test mocks the behavior of the
    business logic layer to throw a `PermissionError` and checks if the application
    handles the exception gracefully by providing the expected output message.

    :param runner: The test runner used to execute the command in the application.
    :type runner: Any
    :param bl_mock: The mock object for the business logic layer to simulate
        specific behaviors during the test.
    :type bl_mock: Any
    :return: None
    """
    bl_mock.list_events_without_support.side_effect = PermissionError("interdit")

    result = runner.invoke(cc.list_events_without_support, [])

    assert result.exit_code == 0
    assert "Accès refusé : interdit" in result.output

def test_generic_error(runner, bl_mock):
    """
    Tests the scenario where a generic error occurs during the invocation of the
    `list_events_without_support` command. Mocks the behavior of the `list_events_without_support`
    method to raise an exception and verifies that the proper error handling outputs the correct
    message to the user.

    :param runner: The CLI test runner used to invoke the command.
    :param bl_mock: The mock object for the `business logic` component, which simulates the
        behavior of the `list_events_without_support` function.
    :return: None. The function checks assertions to validate behavior.
    """
    bl_mock.list_events_without_support.side_effect = Exception("oops")

    result = runner.invoke(cc.list_events_without_support, [])

    assert result.exit_code == 0
    assert "Erreur : oops" in result.output