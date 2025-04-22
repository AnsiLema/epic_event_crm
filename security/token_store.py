from pathlib import Path

DEFAULT_TOKEN_FILE = Path.home() / ".epicevents_token"


def save_token(token: str, path: Path = DEFAULT_TOKEN_FILE):
    with open(path, "w") as f:
        f.write(token)


def load_token(path: Path = DEFAULT_TOKEN_FILE) -> str | None:
    if not path.exists():
        return None
    with open(path, "r") as f:
        return f.read()


def delete_token(path: Path = DEFAULT_TOKEN_FILE):
    if path.exists():
        path.unlink()
