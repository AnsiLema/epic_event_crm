import click
from sqlalchemy.orm import sessionmaker
from bl.contract_bl import ContractBL
from cli.auth_decorator import with_auth_payload
from db.session import engine
from datetime import date


contract_cli = click.Group("contract")
Session = sessionmaker(bind=engine)

@contract_cli.command("list")
@click.option("--full", is_flag=True, help="Afficher plus de détails sur les contrats")
@with_auth_payload
def list_contracts(full, current_user):
    """
    List all contracts with optional detailed information.

    This function fetches all contracts using the business logic layer, displaying their
    basic details. If the `full` option is specified, additional details about the
    contracts (client ID and commercial ID) are included. If no contracts are found,
    an appropriate message is displayed.

    :param bool full: Flag to indicate whether to show extended details of contracts.
    :param current_user: The current user executing the command. Provided by the
                         authentication middleware.
    :return: None
    """
    db = Session()
    bl = ContractBL(db)

    try:
        contracts = bl.list_all_contracts()
        if not contracts:
            click.echo("Aucun contrat trouvé.")
            return

        for c in contracts:
            status_label = "✅ Signé" if c.status else "❌ Non signé"
            base = f"Contrat #{c.id} | {status_label} | Montant : {c.total_amount}€ / restant : {c.amount_left}€"

            if full:
                base += f" | ID du client : {c.client_id} | Id du commercial : {c.commercial_id}"

            click.echo(base)

    except Exception as e:
        click.echo(f"Erreur : {e}")

@contract_cli.command("signed")
@with_auth_payload
def list_signed_contracts(current_user):
    """
    Lists all signed contracts for the authenticated user.

    :param current_user: Represents the currently authenticated user; required argument.
    :return: A list of signed contracts associated with the authenticated user.
    """
    db = Session()
    bl = ContractBL(db)

    try:
        contracts = bl.list_signed_contracts(current_user)
        if not contracts:
            click.echo("Aucun contrat signé trouvé.")
            return

        click.echo(" Contrats signés :")
        for c in contracts:
            click.echo(f" - #{c.id} | {c.total_amount}€ / {c.amount_left} | Client : {c.client_id} |"
                       f" Date de création : {c.creation_date}")
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
    db = Session()
    bl = ContractBL(db)

    try:
        contracts = bl.list_unpaid_contract(current_user)
        if not contracts:
            click.echo("Aucun contrat non payé trouvé.")
            return

        click.echo("Contrats non payés :")
        for c in contracts:
            click.echo(f" - #{c.id} | {c.total_amount}€ / restant : {c.amount_left}€ | Client : {c.client_id} |"
                       f" Date de création : {c.creation_date}")
    except Exception as e:
        click.echo(f"Erreur : {e}")

@contract_cli.command("unsigned")
@with_auth_payload
def list_unsigned_contracts(current_user):
    """
    Lists all unsigned contracts for the current user.

    This function fetches and returns a list of contract details that the
    current user has not yet signed. It utilizes authentication details
    from the provided user context and processes the necessary data.

    :param current_user: The authenticated user executing the command.
    :type current_user: User
    :return: A list of unsigned contracts associated with the current user.
    :rtype: List[Contract]
    """
    db = Session()
    bl = ContractBL(db)

    try:
        contracts = bl.list_unsigned_contracts(current_user)
        if not contracts:
            click.echo("Aucun contrat non signé trouvé.")
            return

        click.echo("Contrat non signé")
        for c in contracts:
            click.echo(f" - #{c.id} | {c.total_amount}€ / Restant : {c.amount_left} | Client : {c.client_id} |"
                       f" Date de création : {c.creation_date}")
    except Exception as e:
        click.echo(f"Erreur : {e}")

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
    Creates a new contract for a client based on the provided details. This function integrates
    user input and utilizes business logic to process and store the contract data in the database.
    It also validates the provided inputs, and manages the creation date and status of the contract.
    Outputs a confirmation message with the contract details upon successful creation.

    :param client_id: The unique identifier of the client.
    :type client_id: int
    :param commercial_id: The unique identifier of the commercial agent.
    :type commercial_id: int
    :param total_amount: The total monetary value of the contract in euros.
    :type total_amount: float
    :param amount_left: The remaining amount left to be paid in euros.
    :type amount_left: float
    :param current_user: The current authenticated user executing the command.
    :type current_user: object
    :return: None
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
