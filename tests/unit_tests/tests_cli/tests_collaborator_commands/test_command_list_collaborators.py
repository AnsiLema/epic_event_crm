# tests_cli/test_command_list_collaborator.py
from click.testing import CliRunner
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

import cli.collaborator_commands as cc

# ------------------------------------------------------------------
# 1) Patch unique : on by‑passe l’authentification
# ------------------------------------------------------------------
outer_cb = cc.list_collaborator.callback
inner_cb = outer_cb.__wrapped__               # fonction métier réelle

def bypass_auth(*args, **kwargs):
    kwargs["current_user"] = {"id": 1, "role": "admin"}
    return inner_cb(*args, **kwargs)

cc.list_collaborator.callback = bypass_auth   # patch définitif

# ------------------------------------------------------------------
# 2) Fixtures
# ------------------------------------------------------------------
@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()

@pytest.fixture(autouse=True)
def patch_session():
    with patch("cli.collaborator_commands.Session") as s_cls:
        s_cls.return_value = MagicMock()
        yield s_cls

@pytest.fixture
def patch_bl():
    with patch("cli.collaborator_commands.CollaboratorBL") as bl_cls:
        inst = MagicMock()
        bl_cls.return_value = inst
        yield inst

@pytest.fixture
def allow_rights():
    with patch("cli.collaborator_commands.can_manage_collaborators", return_value=True):
        yield

@pytest.fixture
def deny_rights():
    with patch("cli.collaborator_commands.can_manage_collaborators", return_value=False):
        yield

# ------------------------------------------------------------------
# 3) Tests
# ------------------------------------------------------------------
def test_list_success(runner, patch_bl, allow_rights):
    patch_bl.get_all_collaborators.return_value = [
        SimpleNamespace(name="Jane", email="jane@corp.io", role_name="gestion"),
        SimpleNamespace(name="John", email="john@corp.io", role_name="support"),
    ]

    res = runner.invoke(cc.list_collaborator)

    assert res.exit_code == 0
    assert "Collaborateurs :" in res.output
    assert "Jane" in res.output and "john@corp.io" in res.output


def test_list_no_permission(runner, deny_rights):
    res = runner.invoke(cc.list_collaborator)

    assert res.exit_code == 0
    assert "n'avez pas le droit" in res.output


def test_list_empty(runner, patch_bl, allow_rights):
    patch_bl.get_all_collaborators.return_value = []

    res = runner.invoke(cc.list_collaborator)

    assert res.exit_code == 0
    assert "Aucun collaborateur trouvé" in res.output


def test_list_error(runner, patch_bl, allow_rights):
    patch_bl.get_all_collaborators.side_effect = Exception("DB down")

    res = runner.invoke(cc.list_collaborator)

    assert res.exit_code == 0
    assert "Erreur :" in res.output and "DB down" in res.output