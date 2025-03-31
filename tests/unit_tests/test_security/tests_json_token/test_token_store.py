from pathlib import Path
import pytest
from security.token_store import save_token, load_token, delete_token

TOKEN_FILE = Path("/tmp/test_token_file.txt")

@pytest.fixture(autouse=True)
def setup_and_teardown():
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
    yield
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()

def test_save_token_creates_file():
    token = "test_token_123"
    save_token(token, path=TOKEN_FILE)
    assert TOKEN_FILE.exists()

def test_save_token_stores_correct_content():
    token = "test_token_content"
    save_token(token, path=TOKEN_FILE)
    with open(TOKEN_FILE, "r") as f:
        saved_content = f.read()
    assert saved_content == token

def test_save_token_overwrites_existing_file():
    save_token("initial_token", path=TOKEN_FILE)
    save_token("updated_token", path=TOKEN_FILE)
    with open(TOKEN_FILE, "r") as f:
        assert f.read() == "updated_token"

def test_save_token_handles_empty_token():
    save_token("", path=TOKEN_FILE)
    with open(TOKEN_FILE, "r") as f:
        assert f.read() == ""

def test_load_token_returns_correct_value():
    expected_token = "test_token_content"
    save_token(expected_token, path=TOKEN_FILE)
    loaded_token = load_token(path=TOKEN_FILE)
    assert loaded_token == expected_token

def test_load_token_returns_none_if_file_missing():
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
    loaded_token = load_token(path=TOKEN_FILE)
    assert loaded_token is None

def test_delete_token_removes_file():
    save_token("to_be_deleted", path=TOKEN_FILE)
    assert TOKEN_FILE.exists()

    delete_token(path=TOKEN_FILE)
    assert not TOKEN_FILE.exists()
