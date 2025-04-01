from sqlalchemy.orm import Session
from datetime import date

from models.contract import Contract
from models.collaborator import Collaborator
from models.client import Client


def create_contract(
        db: Session,
        payload: dict,
        client_id: int,
        commercial_id: int,
        total_amount: float,
        amount_left: float,
        is_signed: bool
) -> Contract | None:
    """
    Creates a new contract in the database and returns the created contract
    object. If creation fails, returns None. The contract is associated with
    a specific client by their client_id and includes details such as the
    total amount, remaining amount, and signature status.

    :param db: The database session used to interact with the database.
    :param payload: A dictionary containing the details of the contract to
        be created.
    :param client_id: The unique identifier of the client associated with
        the contract.
    :param commercial_id: The unique identifier of the commercial.
    :param total_amount: The total monetary value of the contract.
    :param amount_left: The remaining unpaid amount of the contract.
    :param is_signed: The signing status of the contract. A value of True
        indicates the contract has been signed, while False indicates it
        has not.
    :return: A Contract object representing the created contract if successful,
        or None if the creation fails.
    """
    if payload["role"] != "gestion":
        print("Accès refusé : seul un gestionnaire peut créer un contrat.")
        return None

    client = db.query(Client).filter_by(id=client_id).first()
    if not client:
        print("Client introuvable.")
        return None

    commercial = db.query(Collaborator).filter_by(id=commercial_id).first()
    if not commercial or commercial.role.name != "commercial":
        print("Collaborateur introuvable ou non commercial.")
        return None

    contract = Contract(
        client_id=client_id,
        commercial_id=commercial_id,
        total_amount=total_amount,
        amount_left=amount_left,
        status=is_signed,
        creation_date=date.today()
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)
    print("Contrat créé.")
    return contract

def update_contract(
        db: Session,
        payload: dict,
        contract_id: int,
        new_client_id: int | None = None,
        new_commercial_id: int | None = None,
        new_total_amount: float | None = None,
        new_amount_left: float | None = None,
        new_status: bool | None = None
) -> Contract | None:
    """
    Updates an existing contract with new information while enforcing access control
    based on the user's role. This function ensures that only authorized users are
    able to modify contract details, and the updates are validated before being applied.

    :param db: Database session used to query and update objects.
    :type db: Session
    :param payload: Dictionary containing details of the current user such as email and role.
    :type payload: dict
    :param contract_id: The unique ID of the contract to be updated.
    :type contract_id: int
    :param new_client_id: The unique ID of the new client to be assigned to the contract, if applicable.
    :type new_client_id: int | None
    :param new_commercial_id: The unique ID of the new commercial representative to be assigned to the contract,
        if applicable and permitted by the user's role.
    :type new_commercial_id: int | None
    :param new_total_amount: The new total amount for the contract, if applicable.
    :type new_total_amount: float | None
    :param new_amount_left: The new remaining amount for the contract, if applicable.
    :type new_amount_left: float | None
    :param new_status: The new status of the contract (e.g., active or inactive), if applicable.
    :type new_status: bool | None
    :return: The updated contract object if the operation is successful, or None if the operation fails
        (e.g., unauthorized access, invalid parameters, or contract not found).
    :rtype: Contract | None
    """
    # Checks data connection
    if "sub" not in payload or "role" not in payload:
        print("Donnés d'identification manquantes")
        return None

    # Retrieve the contract
    contract: Contract | None = db.query(Contract).filter_by(id=contract_id).first()
    if contract is None:  # Vérifiez explicitement que le contrat existe
        print("Contrat introuvable.")
        return None

    # Current user (secured with JWT)
    current_user: Collaborator | None = db.query(Collaborator).filter_by(email=payload["sub"]).first()
    if not current_user:
        print("Utilisateur introuvable.")
        return None

    # Checks permissions
    authorized = False
    if payload["role"] == "gestion":
        authorized = True
    elif payload["role"] == "commercial" and contract.client and contract.client.commercial_id == current_user.id:
        authorized = True

    if not authorized:
        print("Vous n'avez pas le droit de modifier ce contrat.")
        return None

    # Update fields
    if new_total_amount is not None:
        contract.total_amount = new_total_amount
    if new_amount_left is not None:
        contract.amount_left = new_amount_left
    if new_status is not None:
        contract.status = new_status

    # Update user's id
    if new_client_id is not None:
        client = db.query(Client).filter_by(id=new_client_id).first()
        if not client:
            print(" Client cible introuvable.")
            return None
        contract.client = client

    # Update the commercial's id (by the management team only)
    if payload["role"] == "gestion" and new_commercial_id is not None:
        commercial = db.query(Collaborator).filter_by(id=new_commercial_id).first()
        if not commercial:
            print(" Collaborateur cible introuvable.")
            return None
        if not commercial.role or commercial.role.name != "commercial":
            print(" Le collaborateur ciblé n’a pas le rôle commercial.")
            return None
        contract.commercial = commercial

    db.commit()
    db.refresh(contract)
    print("Contrat mis à jour.")
    return contract
