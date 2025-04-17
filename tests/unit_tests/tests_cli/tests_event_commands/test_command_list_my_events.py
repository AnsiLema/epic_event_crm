import pytest
from click.testing import CliRunner
from types import SimpleNamespace
from datetime import datetime
from unittest.mock import MagicMock, patch

import cli.event_commands as cc


# Bypass decorator @with_auth_payload
_outer_cb = cc.list_my_events.callback
_inner_fn = _outer_cb.__wrapped__

def _bypass_auth(*args, **kwargs):
    # injects a dummy current_user
    return _inner_fn(current_user={"id": 1, "role": "support"})

cc.list_my_events.callback = _bypass_auth


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
def test_no_events_assigned(runner, bl_mock):
    """
    Tests the scenario where no events are assigned to the user. This test ensures
    that the program correctly informs the user that no events are assigned to
    them when the response from the business logic mock indicates an empty list
    of events for the current support.

    :param runner: The Click CLI test runner used to invoke the command.
    :type runner: click.testing.CliRunner
    :param bl_mock: Mock object for the business logic layer used to simulate
        the underlying functionality.
    :type bl_mock: unittest.mock.Mock
    :return: None
    """
    bl_mock.list_events_for_current_support.return_value = []

    result = runner.invoke(cc.list_my_events, [])

    assert result.exit_code == 0
    assert "Aucun événement ne vous est assigné." in result.output

def test_list_my_events_success(runner, bl_mock):
    """
    Tests the successful execution of the `list_my_events` command, ensuring that the output
    correctly displays a list of upcoming events. This function mocks event data
    returned by the business layer and validates that the command-line interface
    produces the expected output.

    :param runner: A test runner used to invoke the CLI command.
    :type runner: pytest fixture or compatible CLI runner
    :param bl_mock: A mock object for the business layer, simulating the behavior of
        methods that interact with event-related operations.
    :type bl_mock: unittest.mock.Mock or compatible mock object
    :return: None
    :rtype: NoneType
    """
    e1 = SimpleNamespace(
        id=201,
        start_date=datetime(2025, 6, 1, 10, 0),
        end_date=datetime(2025, 6, 1, 12, 0),
        location="Salle C"
    )
    e2 = SimpleNamespace(
        id=202,
        start_date=datetime(2025, 6, 2, 14, 0),
        end_date=datetime(2025, 6, 2, 15, 30),
        location="Salle D"
    )
    bl_mock.list_events_for_current_support.return_value = [e1, e2]

    result = runner.invoke(cc.list_my_events, [])

    assert result.exit_code == 0
    assert "Vos événements à venir :" in result.output

    line1 = (
        f"- ID #{e1.id} | Début : {e1.start_date.strftime('%Y-%m-%d %H:%M')} "
        f"| Fin : {e1.end_date.strftime('%Y-%m-%d %H:%M')} | Lieu : {e1.location}"
    )
    line2 = (
        f"- ID #{e2.id} | Début : {e2.start_date.strftime('%Y-%m-%d %H:%M')} "
        f"| Fin : {e2.end_date.strftime('%Y-%m-%d %H:%M')} | Lieu : {e2.location}"
    )
    assert line1 in result.output
    assert line2 in result.output

def test_permission_error(runner, bl_mock):
    """
    Test the behavior of the system when a `PermissionError` is raised by the business logic mock.

    This function is designed to simulate a scenario where access is denied, and ensures the system
    correctly handles the exception by displaying an appropriate error message.

    :param runner: The command-line runner provided by the testing framework to execute CLI commands.
    :type runner: Any
    :param bl_mock: The business logic mock object used to simulate the behavior of the backend service.
    :type bl_mock: Mock
    :return: None
    :rtype: None
    """
    bl_mock.list_events_for_current_support.side_effect = PermissionError("interdit")

    result = runner.invoke(cc.list_my_events, [])

    assert result.exit_code == 0
    assert "Accès refusé : interdit" in result.output

def test_generic_error(runner, bl_mock):
    """
    Test the behavior of the "list_my_events" command in the case of a generic exception
    raised by the business logic mock. This ensures that the output message is correctly
    formatted and the program handles unexpected errors gracefully.

    :param runner: CLI runner instance used for invoking the command to be tested
    :type runner: CliRunner
    :param bl_mock: Mock object for business logic with predefined side effects
    :type bl_mock: mock.Mock
    :return: None
    """
    bl_mock.list_events_for_current_support.side_effect = Exception("oops")

    result = runner.invoke(cc.list_my_events, [])

    assert result.exit_code == 0
    assert "Erreur : oops" in result.output