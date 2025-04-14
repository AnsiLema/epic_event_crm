import click
from sqlalchemy.orm import sessionmaker
from db.session import engine
from models.role import Role
from models.collaborator import Collaborator
from security.password import hash_password

init_cli = click.Group("init")
Session = sessionmaker(bind=engine)

@init_cli.command("all")
def init_all():
    """
    This function initializes the database with predefined roles and a default admin user if they
    do not already exist. Specifically, it creates roles "gestion", "commercial", and "support",
    and an admin user with the "gestion" role using a pre-defined password.

    :raises RuntimeError: If the "gestion" role cannot be found when creating the admin user.

    :returns: None
    """
    db = Session()

    # Creates roles when not existing
    existing_roles = Session().query(Role).all()
    if not existing_roles:
        for role_name in ["gestion", "commercial", "support"]:
            db.add(Role(name=role_name))
        db.commit()
        click.echo("Rôles créés.")
    else:
        click.echo("Les rôles existent déjà.")

    # Creates a first admin user with a management role if non existant
    admin_email = "admin@epicevents.fr"
    existing_admin = Session().query(Collaborator).filter_by(email=admin_email).first()

    if not existing_admin:
        gestion_role = db.query(Role).filter_by(name="gestion").first()
        if not gestion_role:
            click.echo("Rôle 'gestion' introuvable.")
            return

        password = hash_password("admin123")
        admin_user = Collaborator(
            name="Admin",
            email=admin_email,
            password=password,
            role_id=gestion_role.id
        )
        db.add(admin_user)
        db.commit()
        click.echo("Admin créé : {admin_email} / admin123")
    else:
        click.echo("Un admin existe déjà.")