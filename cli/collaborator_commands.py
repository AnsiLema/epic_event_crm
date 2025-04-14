import click
from sqlalchemy.orm import sessionmaker
from bl.collaborator_bl import CollaboratorBL
from cli.auth_decorator import with_auth_payload
from db.session import engine


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
              prompt="Rôle"
)
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
        click.echo(f"ERREUR : {e}")
