import os
from pathlib import Path

TOKEN_FILE = Path.home() / ".epicevents_token"

def save_token(token: str):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

def load_token() -> str | None:
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return f.read()

def delete_token():
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()