import click
import sentry_sdk
from sqlalchemy.orm import sessionmaker
from bl.client_bl import ClientBLL
from cli.auth_decorator import with_auth_payload
from db.session import engine


client_cli = click.Group("client")
Session = sessionmaker(bind=engine)


@client_cli.command("create")
@click.option("--name", prompt="Entrez le nom du client", help="Nom du client")
@click.option("--email", prompt="Entrez l'email du client", help="Email du client")
@click.option("--phone", prompt="Numéro de téléphone", default="", show_default=False)
@click.option("--company", prompt="Nom de l'entreprise", default="", show_default=False)
@with_auth_payload
def create_client(name, email, phone, company, current_user):
    db = Session()
    bl = ClientBLL(db)

    try:
        client = bl.create_client_from_input(
            name=name,
            email=email,
            phone=phone,
            company=company,
            current_user=current_user
        )
        click.echo(f"Client créé : {client.name} ({client.email})")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")


@client_cli.command("list")
@with_auth_payload
def list_clients(current_user):
    """
    Lists all clients associated with the current user.

    This function retrieves all client details from the database
    and displays their names, email addresses, and associated
    companies in the command-line interface. If no clients
    are found, a corresponding message is displayed. In case
    of an error during data retrieval, the error message is
    output.

    :param current_user: Current authenticated user.
    :type current_user: Any
    :return: None
    """
    db = Session()
    bl = ClientBLL(db)

    try:
        clients = bl.get_all_clients()
        if not clients:
            click.echo("Aucun client trouvé.")
            return
        for client in clients:
            click.echo(f"{client.name} - {client.email} | {client.company or 'Non renseigné'}")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")


@client_cli.command("update")
@click.argument("client_id", type=int)
@click.option("--name", help="Nouveau nom du client")
@click.option("--email", help="Nouveau email du client")
@click.option("--phone", help="Nouveau numéro de téléphone")
@click.option("--company", help="Nouveau nom de l'entreprise")
@with_auth_payload
def update_client(client_id, name, email, phone, company, current_user):
    """
    Update an existing client's information in the system.

    This function serves as a command-line interface command utilizing `click`. It
    interacts with the database to update client details based on the provided
    inputs for `name`, `email`, `phone`, and `company`. The `current_user` is
    utilized for authorization purposes. The updated client details are then
    displayed via the CLI.

    :param client_id: Identifier of the client to be updated.
    :type client_id: int
    :param name: New name of the client.
    :param email: New email address of the client.
    :param phone: New phone number of the client.
    :param company: New name of the company associated with the client.
    :param current_user: Currently authenticated user performing the update.
    :return: None
    """
    db = Session()
    bl = ClientBLL(db)

    try:
        client = bl.get_client(client_id)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")
        return

    click.echo(f"📝 Client actuel : {client.name} ({client.email}) - {client.company or 'N/A'}")

    if not name:
        name = click.prompt("Nom du client", default=client.name)
    if not email:
        email = click.prompt("Email du client", default=client.email)
    if not phone:
        phone = click.prompt("Téléphone", default=client.phone or "")
    if not company:
        company = click.prompt("Société", default=client.company or "")

    updates = {
        "name": name,
        "email": email,
        "phone": phone,
        "company": company,
    }

    try:
        updated = bl.update_client(client_id, updates, current_user)
        click.echo(f"Client mis à jour : {updated.name} ({updated.email})")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")
