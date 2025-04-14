import click
from sqlalchemy.orm import sessionmaker
from bl.contract_bl import ContractBL
from cli.auth_decorator import with_auth_payload
from db.session import engine
from datetime import date


contract_cli = click.Group("contract")
Session = sessionmaker(bind=engine)

@contract_cli.command("list")
@click.option("--signed", is_flag=True, help="Afficher uniquement les contrats signés")
@click.option("--unsigned", is_flag=True, help="Afficher uniquement les contrats non signés")
@click.option("--full", is_flag=True, help="Afficher plus de détails sur les contrats")
@with_auth_payload
def list_contracts(signed, unsigned, full, current_user):
    """
    Displays a list of contracts based on specific filters and options. The user can filter only
    signed contracts, only unsigned contracts, or view all contracts. Additional detailed information
    can be displayed based on the provided options. Ensures that two conflicting filters cannot
    be applied simultaneously. Handles errors gracefully by displaying appropriate error messages.

    :param signed: Flag to filter and display only signed contracts.
    :type signed: bool
    :param unsigned: Flag to filter and display only unsigned contracts.
    :type unsigned: bool
    :param full: Flag to display additional details for each contract.
    :type full: bool
    :param current_user: The current authenticated user making the request.
    :return: Outputs a formatted list of contracts based on specified filter flags.
    :rtype: None
    """
    db = Session()
    bl = ContractBL(db)

    try:
        if signed and unsigned:
            click.echo("Erreur : Vous ne pouvez pas utiliser les 2 filtres en même temps.")
            return

        if signed:
            contracts = bl.list_signed_contracts()
        elif unsigned:
            contracts = bl.list_unsigned_contracts()
        else:
            contracts = bl.list_all_contracts()

        if not contracts:
            click.echo("Aucun contrat trouvé.")
            return

        for c in contracts:
            status_label = "✓ Signé" if c.status else "ｘ Non signé"
            base = f"Contrat #{c.id} | {status_label} | Montant : {c.total_amount}€ / restant : {c.amount_left}€"

            if full:
                base += f" | ID du client : {c.client_id} | Id du commercial : {c.commercial_id} "

            click.echo(base)

    except Exception as e:
        click.echo(f"Erreur : {e}")

@contract_cli.command("unpaid")
@with_auth_payload
def list_unpaid_contracts(current_user):
    """
    Lists all unpaid contracts for the current user.

    This function retrieves a list of contracts that are unpaid
    for the currently authenticated user. The user information
    is provided through the `current_user` parameter. Mainly used
    in CLI environments where authenticated users need to manage
    their contracts.

    :param current_user: Represents the authenticated user making the
        request and whose unpaid contracts will be listed.
    :return: Returns a list of contracts that are currently unpaid
        for the given user.
    """

@contract_cli.command("create")
@click.option("--client-id", type=int,
              prompt="Entrez l'identifiant du client",
              help="Identifiant du client")
@click.option("--commercial-id", type=int,
              prompt="Entrez l'identifiant du commercial",
              help="Identifiant du commercial")
@click.option("--total-amount", type=float, prompt="Montant du contrat", help="Montant du contrat(en €)")
@click.option("--amount-left", type=float, prompt="Montant restant à payer", help="Montant restant(en €)")
@with_auth_payload
def create_contract(client_id, commercial_id, total_amount, amount_left, current_user):
    """
    """
    db = Session()
    bl = ContractBL(db)

    try:
        contract_data = {
            "client_id": client_id,
            "commercial_id": commercial_id,
            "total_amount": total_amount,
            "amount_left": amount_left,
            "creation_date": date.today(),
            "status": False
        }

        contract = bl.create_contract(contract_data, current_user)
        click.echo(f"Contrat créé : #{contract.id} -  Montant : {contract.total_amount}€, Statut : Non Signé")

    except Exception as e:
        click.echo(f"Erreur : {e}")

@contract_cli.command("update")
@click.argument("contract_id", type=int)
@with_auth_payload
def update_contract(contract_id, current_user):
    """
    Handles the update of a contract using command-line options and prompts.

    This command interacts with the database to retrieve and modify contract details.
    It allows the user to specify new values for the total amount, amount left, and the
    status of the contract. The updated data is persisted in the database, and the updated
    contract details are displayed back to the user.

    :param contract_id: ID of the contract to be updated.
    :type contract_id: int
    :param current_user: The user executing the update command, used for authorization purposes.
    :type current_user: User
    :return: None
    """
    db = Session()
    bl = ContractBL(db)

    click.echo(f"Payload reçu : {current_user}") # DEBUG temporaire

    try:
        contract = bl.get_contract(contract_id)
    except Exception as e:
        click.echo(f"Erreur : {e}")
        return

    status_label = "✅ Signé" if contract.status else "❌ Non signé"
    click.echo(f"Contrat Actuel : #{contract.id}")
    click.echo(f" - Montant total   : {contract.total_amount}")
    click.echo(f" - Montant restant : {contract.amount_left}")
    click.echo(f" - Statut          : {status_label}")

    try:
        total_amount = click.prompt("Nouveau montant du contrat", default=contract.total_amount, type=float)
        amount_left = click.prompt("Nouveau montant restant", default=contract.amount_left, type=float)
        status = click.confirm("Nouveau statut du contrat", default=contract.status)

        updates = {
            "total_amount": total_amount,
            "amount_left": amount_left,
            "status": status
        }

        updated = bl.update_contract(contract_id, updates, current_user)

        label = "✅ Signé" if updated.status else "❌ Non signé"
        click.echo(f"Contrat mis à jour : #{updated.id} | Total : {updated.total_amount}€, Statut : {label}")

    except Exception as e:
        click.echo(f"Erreur pendant la mis à jour: {e}")

@contract_cli.command("show")
@click.argument("contract_id", type=int)
@with_auth_payload
def show_contract_detail(contract_id, current_user):
    """
    Displays the details of a specific contract.

    This function retrieves and outputs detailed information about a contract
    specified by its unique contract ID. User authentication is required
    to access the contract details.

    :param contract_id: The unique identifier for the contract.
    :param current_user: The user currently authenticated and requesting
        the contract details.
    :return: None
    """
    db = Session()
    bl = ContractBL(db)

    try:
        contract = bl.get_contract(contract_id)
    except Exception as e:
        click.echo(f"Erreur : {e}")
        return

    click.echo(f"Contrat #{contract.id} :")
    click.echo(f" - Montant total   : {contract.total_amount}")
    click.echo(f" - Montant restant : {contract.amount_left}")
    click.echo(f" - Statut          : {'✅ Signé' if contract.status else '❌ Non signé'}")
    click.echo(f"  - ID du client   : {contract.client_id}")
    click.echo(f"  - ID du commercial : {contract.commercial_id}")

