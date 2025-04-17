from click.testing import CliRunner
from unittest.mock import MagicMock, patch
import pytest

from cli import client_commands as cc

_original = cc.update_client.callback
_inner = _original.__wrapped__

def _dummy_cb(client_id, name, email, phone, company):
    return _inner(client_id, name, email, phone, company, MagicMock(name="user"))

cc.update_client.callback = _dummy_cb

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def fake_client():
    c = MagicMock()
    c.id = 1
    c.name = "Old"
    c.email = "old@corp.io"
    c.phone = "0600000000"
    c.company = "Old Corp"
    return c

@pytest.fixture
def patch_bll(fake_client):
    with patch("cli.client_commands.ClientBLL") as bcls:
        bll = MagicMock()
        bll.get_client.return_value = fake_client
        bcls.return_value = bll
        yield bll

@pytest.fixture(autouse=True)
def patch_session():
    with patch("cli.client_commands.Session") as scls:
        scls.return_value = MagicMock()
        yield scls

def test_update_client_success(runner, patch_bll):
    up = MagicMock()
    up.name = "New"
    up.email = "new@corp.io"
    patch_bll.update_client.return_value = up

    res = runner.invoke(
        cc.update_client,
        [
            "1",
            "--name", "New",
            "--email", "new@corp.io",
            "--phone", "0707070707",
            "--company", "New Corp",
        ],
    )

    assert res.exit_code == 0
    assert "Client mis à jour : New (new@corp.io)" in res.output
    patch_bll.update_client.assert_called_once()

def test_update_client_prompts(runner, patch_bll, fake_client):
    patch_bll.update_client.return_value = fake_client
    answers = "\n".join(["Jean", "jean@corp.fr", "0612345678", "Jean Corp"]) + "\n"
    res = runner.invoke(cc.update_client, ["1"], input=answers)

    assert res.exit_code == 0
    assert "Client mis à jour" in res.output
    kwargs = patch_bll.update_client.call_args.args[1]
    assert kwargs["name"] == "Jean"
    assert kwargs["phone"] == "0612345678"

def test_update_client_not_found(runner):
    with patch("cli.client_commands.ClientBLL") as bcls:
        bll = MagicMock()
        bll.get_client.side_effect = Exception("Client introuvable")
        bcls.return_value = bll
        res = runner.invoke(cc.update_client, ["1"])
    assert res.exit_code == 0
    assert "Erreur : Client introuvable" in res.output

def test_update_client_permissions_error(runner, patch_bll):
    patch_bll.update_client.side_effect = PermissionError("Interdit")
    res = runner.invoke(cc.update_client, ["1", "--name", "X"])
    assert res.exit_code == 0
    assert "Interdit" in res.output