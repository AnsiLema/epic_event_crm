import click
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
        click.echo(f"Erreur : {e}")