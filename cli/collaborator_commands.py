import click
import sentry_sdk
from sqlalchemy.orm import sessionmaker
from bl.collaborator_bl import CollaboratorBL
from cli.auth_decorator import with_auth_payload
from db.session import engine
from security.permissions import can_manage_collaborators

collaborator_cli = click.Group("collaborator")
Session = sessionmaker(bind=engine)


@collaborator_cli.command("create")
@click.option("--name", prompt="Entrez le nom du collaborateur", help="Nom du collaborateur")
@click.option("--email", prompt="Entrez l'email du collaborateur", help="Email du collaborateur")
@click.option("--password", prompt="Création du mot de passe du collaborateur", hide_input=True,
              confirmation_prompt="Retapez le mot de passe pour confirmer",
              help="Mot de passe du collaborateur")
@click.option("--role",
              type=click.Choice(["gestion", "support", "commercial"]),
              prompt="Rôle")
@with_auth_payload
def create_collaborator(name, email, password, role, current_user):
    """
    Create a new collaborator through CLI with necessary inputs and options.

    This function allows the user to create a collaborator by providing inputs such
    as name, email, password, and role through the terminal. The creation process
    is processed via a business logic layer, which interacts with the database.
    Proper authentication is required before execution. Any errors during the
    creation process are captured and displayed to the user.

    :param name: Name of the collaborator.
    :type name: str
    :param email: Email of the collaborator.
    :type email: str
    :param password: Password for the collaborator.
    :type password: str
    :param role: Role assigned to the collaborator, which must be chosen from
        "gestion", "support", and "commercial".
    :type role: str
    :param current_user: Authenticated user performing the operation.
    :type current_user: dict
    :return: None
    """
    db = Session()
    bl = CollaboratorBL(db)

    try:
        collab = bl.create_collaborator_from_input(
            name=name,
            email=email,
            password=password,
            role_name=role,
            current_user=current_user
        )
        click.echo(f"Collaborateur créé : {collab.name} ({collab.email}) - Rôle : {collab.role_name}")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"ERREUR : {e}")


@collaborator_cli.command("list")
@with_auth_payload
def list_collaborator(current_user):
    """
    Lists all collaborators associated with the current user.

    This command fetches and displays all collaborators tied to the current user's
    account. Authentication is required to execute this command.

    :param current_user: The user currently logged into the system, provided by
        the authentication payload.
    :return: A list of collaborators related to the current user's account.
    :rtype: list
    """
    db = Session()
    bl = CollaboratorBL(db)

    if not can_manage_collaborators(current_user):
        click.echo("Vous n'avez pas le droit d'afficher la liste des collaborateurs.")
        return

    try:
        collaborators = bl.get_all_collaborators()
        if not collaborators:
            click.echo("Aucun collaborateur trouvé.")
            return

        click.echo("Collaborateurs : ")
        for c in collaborators:
            click.echo(f" - {c.name} - {c.email} - rôle : {c.role_name}")

    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")


@collaborator_cli.command("update")
@click.argument("collaborator_id", type=int)
@with_auth_payload
def update_collaborator(collaborator_id, current_user):
    """
    Updates collaborator information in the system using the provided identifier.

    This function is responsible for updating existing collaborator details
    based on the provided collaborator ID. It requires authentication, verified
    through the `current_user` parameter. This allows authorized users to make
    changes to a collaborator's data in the system.

    :param collaborator_id: The unique identifier of the collaborator to update.
    :type collaborator_id: int
    :param current_user: The authenticated user making the request. Represents
        the user performing the operation.
    :return: A confirmation of the update operation or status information.
    """
    db = Session()
    bl = CollaboratorBL(db)

    try:
        collab = bl.get_by_id(collaborator_id)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")
        return

    click.echo(f"Collaborateur actuel : {collab.name} ({collab.email}) - rôle : {collab.role_name}")

    name = click.prompt("Nouveau nom", default=collab.name)
    email = click.prompt("Nouvel email", default=collab.email)
    role = click.prompt("Nouveau rôle", type=click.Choice(["gestion", "support", "commercial"]),
                        default=collab.role_name)

    updates = {
        "name": name,
        "email": email,
        "role_name": role
    }

    try:
        updated = bl.update_collaborator(collaborator_id, updates, current_user)
        click.echo(f"Collaborateur mis à jour : {updated.name} ({updated.email}) - rôle : {updated.role_name}")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur lors de la mise à jour : {e}")


@collaborator_cli.command("delete")
@click.argument("collaborator_id", type=int)
@with_auth_payload
def delete_collaborator(collaborator_id, current_user):
    """
    Deletes a collaborator from the system based on their unique identifier. This
    function interacts with the business logic layer to fetch and delete the
    specified collaborator. It includes user confirmation before the deletion
    process is executed and provides feedback upon completion or failure.

    :param collaborator_id: The unique identifier of the collaborator to be deleted.
    :type collaborator_id: int
    :param current_user: The authenticated user requesting the deletion operation.
    :type current_user: Any
    :return: None
    """
    db = Session()
    bl = CollaboratorBL(db)

    try:
        collab = bl.get_by_id(collaborator_id)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")
        return

    click.echo(f"⚠️ Vous êtes sur le point de supprimer : {collab.name} ({collab.email}) - rôle : {collab.role_name}")
    if not click.confirm("Voulez-vous vraiment supprimer cet utilisateur ?", default=False):
        click.echo("Suppression annulée.")
        return

    try:
        bl.delete_collaborator(collaborator_id, current_user)
        click.echo("Collaborateur supprimé avec succès.")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur lors de la suppression : {e}")
