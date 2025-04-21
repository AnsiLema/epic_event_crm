# tests/unit_tests/tests_cli/tests_event_commands/test_create_event_command.py
from click.testing import CliRunner
from types import SimpleNamespace
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest

import cli.event_commands as cc


# Bypass du décorateur @with_auth_payload

_outer_cb = cc.create_event.callback
_inner_cb = _outer_cb.__wrapped__

def _bypass_auth(*args, **kwargs):
    # injects a dummy curent user
    return _inner_cb(current_user={"id": 1, "role": "admin"})

cc.create_event.callback = _bypass_auth


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

def test_create_event_success(runner, bl_mock):
    """
    Tests successful creation of an event through a CLI command.

    This test simulates the process of creating an event where user
    input is mocked using predefined prompts. The mocked `create_event`
    method of the event business logic (BL) returns a fake event
    object. Additionally, it verifies the correctness of data passed
    to the BL, such as contract ID, start and end dates, location,
    number of attendees, and optional note. It also checks the CLI success
    message and result exit code.

    :param runner: CLI test runner fixture used to invoke the command.
    :type runner: Any
    :param bl_mock: Mock for business logic handling event creation.
    :type bl_mock: MagicMock
    :return: None
    :rtype: None
    """
    evt = SimpleNamespace(id=77, contract_id=33)
    bl_mock.create_event.return_value = evt

    # Prompts : contract_id, start_str, end_str, location, attendees, note
    prompts = [
        33,
        "2025-05-01 10:00",
        "2025-05-01 12:00",
        "Salle A",
        20,
        ""
    ]

    with patch("cli.event_commands.click.prompt", side_effect=prompts):
        res = runner.invoke(cc.create_event, [])

    assert res.exit_code == 0
    assert f"Évènement crée (ID #{evt.id}) pour le contrat {evt.contract_id}" in res.output

    data_arg, user_arg = bl_mock.create_event.call_args[0]
    assert data_arg["contract_id"] == 33
    assert isinstance(data_arg["start_date"], datetime)
    assert data_arg["start_date"] == datetime(2025, 5, 1, 10, 0)
    assert data_arg["end_date"] == datetime(2025, 5, 1, 12, 0)
    assert data_arg["location"] == "Salle A"
    assert data_arg["attendees"] == 20
    assert data_arg["note"] is None  # empty string becomes None
    assert user_arg == {"id": 1, "role": "admin"}

def test_create_event_with_note(runner, bl_mock):
    """
    Test case to validate the creation of an event with an accompanying note. This function
    mocks necessary inputs and dependencies to simulate the behavior of the event creation
    command-line interface (CLI). The function assesses whether the event creation executes
    successfully, and ensures the note information is correctly passed to the backend logic.

    :param runner: The CLI testing runner used to simulate command-line interactions.
    :type runner: click.testing.CliRunner
    :param bl_mock: The mock object for the backend logic, simulating service methods in
        the business logic layer.
    :type bl_mock: unittest.mock.Mock
    :return: None
    """
    evt = SimpleNamespace(id=88, contract_id=44)
    bl_mock.create_event.return_value = evt

    prompts = [
        "44",
        "2025-06-01 09:30",
        "2025-06-01 11:00",
        "Salle B",
        "15",
        "Réunion projet"   # non-empty note
    ]

    with patch("cli.event_commands.click.prompt", side_effect=prompts):
        res = runner.invoke(cc.create_event, [])

    assert res.exit_code == 0
    assert "Évènement crée (ID #88) pour le contrat 44" in res.output
    data_arg, _ = bl_mock.create_event.call_args[0]
    assert data_arg["note"] == "Réunion projet"

@pytest.mark.parametrize("exc,msg", [
    (ValueError("Donnée invalide"), "Donnée invalide"),
    (Exception("Erreur serveur"), "Erreur serveur"),
])
def test_create_event_error(runner, bl_mock, exc, msg):
    """
    Test function for verifying error handling in event creation.

    This test function validates the behavior of the `create_event` functionality
    when exceptions are raised by the `create_event` method in the business layer.
    It checks if the appropriate error message corresponding to the raised exception
    is displayed in the command-line output.

    :param runner: Test runner object provided by the testing framework.
    :type runner: pytest.FixtureRequest
    :param bl_mock: Mock object for business layer functionality, specifically
        mocking `create_event` behavior.
    :type bl_mock: unittest.mock.Mock
    :param exc: Exception instance that is raised during the test to simulate
        an error condition in the business logic.
    :type exc: Exception
    :param msg: Expected error message to be displayed as feedback to the user.
    :type msg: str
    :return: None
    """
    bl_mock.create_event.side_effect = exc

    # We still answer the prompts, but the exception occurs at the call
    prompts = ["1", "2025-07-01 08:00", "2025-07-01 09:00", "X", "5", ""]
    with patch("cli.event_commands.click.prompt", side_effect=prompts):
        res = runner.invoke(cc.create_event, [])

    assert res.exit_code == 0
    assert f"Erreur : {msg}" in res.output