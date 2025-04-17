# tests/unit_tests/tests_cli/tests_event_commands/test_list_all_events_command.py

import pytest
from click.testing import CliRunner
from types import SimpleNamespace
from datetime import datetime
from unittest.mock import MagicMock, patch

import cli.event_commands as cc


# Bypass decorator @with_auth_payload
_outer_cb = cc.list_all_events.callback
_inner_fn = _outer_cb.__wrapped__

def _bypass_auth(*args, **kwargs):
    # injects a dummy current_user
    return _inner_fn(current_user={"id": 1, "role": "admin"})

cc.list_all_events.callback = _bypass_auth


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
def test_no_events_registered(runner, bl_mock):
    """Quand BL renvoie [], on affiche 'Aucun événement enregistré.'"""
    bl_mock.list_all_events.return_value = []

    result = runner.invoke(cc.list_all_events, [])

    assert result.exit_code == 0
    assert "Aucun événement enregistré." in result.output

def test_list_all_events_success(runner, bl_mock):
    """
    This function is a test case that verifies the correct functioning of the
    `list_all_events` command by simulating a successful scenario. The test ensures
    that the command returns the list of events provided by the mocked business
    logic and displays the details of each event in the expected output format. The
    test uses `runner` for executing the command-line interface command and
    `bl_mock` to simulate the behavior of the business logic.

    :param runner: The test runner used to invoke the command-line interface commands.
    :param bl_mock: A mock object representing the business logic layer, used to
        simulate event data for the purpose of the test.
    :return: None. The function only performs assertions to validate the behavior
        of the code under test.
    """
    e1 = SimpleNamespace(
        id=1,
        start_date=datetime(2025, 7, 1, 9, 0),
        end_date=datetime(2025, 7, 1, 11, 0),
        location="Salle 1",
        attendees=10,
        support_id=5
    )
    e2 = SimpleNamespace(
        id=2,
        start_date=datetime(2025, 7, 2, 14, 0),
        end_date=datetime(2025, 7, 2, 16, 0),
        location="Salle 2",
        attendees=20,
        support_id=None
    )
    bl_mock.list_all_events.return_value = [e1, e2]

    result = runner.invoke(cc.list_all_events, [])

    assert result.exit_code == 0
    # Vérifie l'en-tête
    assert "Tous les événements :" in result.output

    line1 = (
        f"- ID #{e1.id} | {e1.start_date.strftime('%Y-%m-%d %H:%M')} → "
        f"{e1.end_date.strftime('%Y-%m-%d %H:%M')} | Lieu : {e1.location} | "
        f"Participants : {e1.attendees} | Support : {e1.support_id}"
    )
    assert line1 in result.output

    # Ligne pour e2 inclut "Aucun support"
    line2 = (
        f"- ID #{e2.id} | {e2.start_date.strftime('%Y-%m-%d %H:%M')} → "
        f"{e2.end_date.strftime('%Y-%m-%d %H:%M')} | Lieu : {e2.location} | "
        f"Participants : {e2.attendees} | Aucun support"
    )
    assert line2 in result.output

def test_list_all_events_error(runner, bl_mock):
    """
    Tests the behavior of the `list_all_events` command when an exception is raised
    by the mocked backend layer, simulating a database failure. Ensures appropriate
    error handling and user feedback are implemented.

    :param runner: Provides a testing CLI runner to invoke CLI commands.
    :param bl_mock: Mocked instance of the backend layer to simulate specific
        behaviors or exceptions.
    :return: No explicit return value, the test verifies behavior through assertions.
    """
    bl_mock.list_all_events.side_effect = Exception("BDD down")

    result = runner.invoke(cc.list_all_events, [])

    assert result.exit_code == 0
    assert "Erreur : BDD down" in result.output