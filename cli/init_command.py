import click
import sentry_sdk
from sqlalchemy.orm import sessionmaker
from db.session import SessionLocal
from bl.role_bl import RoleBL
from bl.collaborator_bl import CollaboratorBL
from security.password import hash_password


init_cli = click.Group("init")

@click.command("all")
def init_all():
  db = SessionLocal()
  try:
      role_bl = RoleBL(db)
      collaborator_bl = CollaboratorBL(db)

      # Creation of roles if non-existing
      created_roles = []
      for role in ["gestion", "commercial", "support"]:
          try:
              role_bl.create_role(role)
              created_roles.append(role)
          except ValueError:
              continue # Role already exists

      if created_roles:
          click.echo(f"Rôles crées : {', '.join(created_roles)}")
      else:
          click.echo("Les rôles existent déjà.")

      # Creation of admin if non-existing
      admin_email = "admin@epicevents.fr"
      existing_admin = collaborator_bl.dal.get_by_email_raw(admin_email)

      if not existing_admin:
          password = click.prompt("Mot de passe de l'administrateur", hide_input=True, confirmation_prompt=True)
          hashed_pw = hash_password(password)

          gestion_role = role_bl.get_gestion_role()
          if not gestion_role:
              click.echo("Rôle 'gestion' introuvable. Initialisation interrompue.")
              return

          collaborator_bl.create_collaborator({
              "name": "Admin",
              "email": admin_email,
              "password": hashed_pw,
              "role_id": gestion_role.id
          })
          click.echo("Admin créé : admin@epicevents.fr")
      else:
          click.echo("Un administrateur existe déjà.")

  except Exception as e:
      sentry_sdk.capture_exception(e)
      click.echo(f"Erreur lors de l'initialisation : {e}")
  finally:
      db.close()

init_cli.add_command(init_all)