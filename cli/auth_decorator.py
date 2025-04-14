import click
from functools import wraps
from security.token_store import load_token
from security.jwt import decode_access_token

def with_auth_payload(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = load_token()
        if not token:
            raise click.ClickException("Vous devez être connecté(e).")

        payload = decode_access_token(token)
        if not payload:
            raise click.ClickException("Token invalide ou expiré.")

        return f(*args, current_user=payload, **kwargs)

    return wrapper