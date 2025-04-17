from click.testing import CliRunner
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

import cli.collaborator_commands as cc

# ---------------------------------------------------------------------
# Patch unique : bypass authentification
# ---------------------------------------------------------------------
_orig = cc.create_collaborator.callback
_inner = _orig.__wrapped__                   # fonction métier réelle

def bypass_auth(*args, **kw):
    kw["current_user"] = {"id": 1, "role": "admin"}
    return _inner(*args, **kw)

cc.create_collaborator.callback = bypass_auth
# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------
@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def session_mock():
    with patch("cli.collaborator_commands.Session") as s:
        s.return_value = MagicMock()
        yield s

@pytest.fixture
def bl_mock():
    with patch("cli.collaborator_commands.CollaboratorBL") as cls:
        inst = MagicMock()
        cls.return_value = inst
        yield inst
# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------
def test_create_success_with_options(runner, bl_mock):
    # objet « collaborateur » valide
    bl_mock.create_collaborator_from_input.return_value = SimpleNamespace(
        name="Jane Doe", email="jane@corp.io", role_name="gestion"
    )

    res = runner.invoke(
        cc.create_collaborator,
        [
            "--name", "Jane Doe",
            "--email", "jane@corp.io",
            "--password", "StrongPwd123",
            "--role", "gestion",
        ],
    )

    assert res.exit_code == 0
    assert "Collaborateur créé" in res.output
    assert "Jane Doe" in res.output
    assert "gestion" in res.output


def test_create_success_via_prompts(runner, bl_mock):
    bl_mock.create_collaborator_from_input.return_value = SimpleNamespace(
        name="John", email="john@corp.io", role_name="support"
    )
    answers = "\n".join(["John", "john@corp.io", "Pwd!2024", "Pwd!2024", "support"]) + "\n"
    res = runner.invoke(cc.create_collaborator, input=answers)

    assert res.exit_code == 0
    assert "John" in res.output
    assert "support" in res.output


@pytest.mark.parametrize(
    "exc, fragment",
    [
        (ValueError("Tous les champs sont requis"), "Tous les champs sont requis"),
        (ValueError("Le rôle 'invalide' n'existe pas."), "rôle 'invalide'"),
        (ValueError("Un collaborateur avec cet email existe déjà."), "cet email existe déjà"),
        (ValueError("Le mot de passe doit contenir au moins 8 caractères."), "8 caractères"),
    ],
)
def test_create_errors(runner, bl_mock, exc, fragment):
    bl_mock.create_collaborator_from_input.side_effect = exc
    dummy = "\n".join(["a", "b", "c", "c", "gestion"]) + "\n"
    res = runner.invoke(cc.create_collaborator, input=dummy)

    assert res.exit_code == 0
    assert "ERREUR" in res.output
    assert fragment in res.output