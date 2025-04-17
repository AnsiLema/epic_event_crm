# tests/unit_tests/tests_cli/tests_init_commands/test_init_all_command.py
import pytest
from click.testing import CliRunner
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import cli.init_command as m  # module contenant init_all

# ---------------------------------------------------------------------------
# FIXTURE pour patcher Session une seule fois
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def session_mock():
    """
    Patch `Session` pour qu'il retourne toujours le même mock de session.
    """
    sess = MagicMock()
    with patch("cli.init_command.Session", return_value=sess):
        yield sess

# ---------------------------------------------------------------------------
# TESTS ----------------------------------------------------------------------
# ---------------------------------------------------------------------------
def test_init_all_creates_roles_and_admin(session_mock):
    # 1) Pas de rôles existants → .query(Role).all() renvoie []
    role_q = MagicMock()
    role_q.all.return_value = []
    # 2) Pas d'admin existant → .query(Collaborator).filter_by().first() renvoie None
    collab_q = MagicMock()
    collab_q.filter_by.return_value.first.return_value = None

    # On fait varier Session().query selon le modèle fourni
    def query_side_effect(model):
        if model.__name__ == "Role":
            return role_q
        else:  # Collaborator
            return collab_q
    session_mock.query.side_effect = query_side_effect

    runner = CliRunner()
    result = runner.invoke(m.init_all, [])

    # Vérifie les échos
    assert "Rôles créés." in result.output
    assert "Admin créé : {admin_email} / admin123" in result.output

    # Vérifie qu'on ait ajouté 3 rôles + 1 admin
    assert session_mock.add.call_count == 4
    # Deux commits : après création des rôles, après création de l'admin
    assert session_mock.commit.call_count == 2

def test_init_all_roles_exist_and_admin_exist(session_mock):
    # 1) Rôles déjà existants → all() renvoie non vide
    role_q = MagicMock()
    role_q.all.return_value = [SimpleNamespace(name="gestion")]
    # 2) Admin déjà existant → first() renvoie un objet truthy
    collab_q = MagicMock()
    collab_q.filter_by.return_value.first.return_value = SimpleNamespace(email="admin@epicevents.fr")

    session_mock.query.side_effect = lambda model: role_q if model.__name__ == "Role" else collab_q

    runner = CliRunner()
    result = runner.invoke(m.init_all, [])

    assert "Les rôles existent déjà." in result.output
    assert "Un admin existe déjà." in result.output

    # Pas d'insert, pas de commit
    session_mock.add.assert_not_called()
    session_mock.commit.assert_not_called()

def test_init_all_roles_exist_but_no_gestion_role(session_mock):
    # 1) Rôles existent (all non vide)
    role_q = MagicMock()
    role_q.all.return_value = ["x"]
    # 2) Pas d'admin existant
    collab_q = MagicMock()
    collab_q.filter_by.return_value.first.return_value = None
    # 3) Pas de rôle 'gestion' trouvé via db.query(Role).filter_by(...)
    #    Ici on réutilise role_q pour Role but we override filter_by.first
    role_q.filter_by.return_value.first.return_value = None

    session_mock.query.side_effect = lambda model: role_q if model.__name__ == "Role" else collab_q

    runner = CliRunner()
    result = runner.invoke(m.init_all, [])

    assert "Les rôles existent déjà." in result.output
    assert "Rôle 'gestion' introuvable." in result.output

    # On n'ajoute pas d'admin
    session_mock.add.assert_not_called()
    session_mock.commit.assert_not_called()

def test_init_all_error_on_role_query(session_mock):
    # Simule une exception dès le premier Session().query(Role)
    session_mock.query.side_effect = Exception("BD KO")

    runner = CliRunner()
    result = runner.invoke(m.init_all, [])

    assert result.exception is not None
    assert "BD KO" in str(result.exception)