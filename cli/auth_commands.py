import click
from sqlalchemy.orm import sessionmaker
from security.auth_service import authenticate_collaborator
from security.jwt import create_access_token, decode_access_token
from security.token_store import save_token, load_token, delete_token
from db.session import engine


auth_cli = click.Group("auth")
Session = sessionmaker(bind=engine)

def require_auth() -> dict:
    """Loads user's payload from token CLI."""
    token = load_token()
    if not token:
        raise click.ClickException("Vous devez vous connecter.")
    payload = decode_access_token(token)
    if not payload:
        raise click.ClickException("Token Invalide ou expiré.")
    return payload

@auth_cli.command("login")
@click.argument("email")
@click.argument("password")
def login(email, password):
    """
    Handles the login operation for the authentication system.

    This command allows a user to log in by providing an email and password. The
    email should correspond to the registered account in the system, and the
    password must match the valid credential information to complete the login process.

    :param email: The email address of the user attempting to log in.
    :type email: str
    :param password: The password associated with the email address.
    :type password: str
    :return: None
    """
    db = Session()
    payload = authenticate_collaborator(db, email, password)

    if not payload:
        click.echo("Identifiants incorrects.")
        return

    token = create_access_token(payload)
    save_token(token)
    click.echo(f"Connecté : {payload['email']} (rôle : {payload['role']})")

@auth_cli.command("logout")
def logout():
    """
    Logs the user out of the system.

    This function ends the user session, whether it is authenticated or not. It ensures
    that any resources or tokens associated with the session are properly invalidated,
    thereby protecting sensitive user data and preventing unauthorized access.

    :return: None
    """
    delete_token()
    click.echo("Déconnecté avec succès.")

@auth_cli.command("whoami")
def whoami():
    """
    Provides functionality to determine and return the identity of the user invoking the
    command. This function is part of the CLI commands defined under `@auth_cli`.

    :return: A string representing the identity of the current user
    :rtype: str
    """
    token = load_token()
    if not token:
        click.echo("Vous devez vous connecter.")
        return

    payload = decode_access_token(token)
    if not payload:
        click.echo("Token invalide ou expiré")
        return

    click.echo(f"👤 Connecté : {payload['email']} (rôle : {payload['role']})")