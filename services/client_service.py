from datetime import date
from sqlalchemy.orm import Session
from models.client import Client
from models.collaborator import Collaborator

def create_client(
        db: Session,
        payload: dict,
        name: str,
        email: str,
        phone: str,
        company: str
) -> Client | None:
    """
    Creates a new client record in the database. If the operation is successful,
    the newly created client is returned. If the operation fails for any reason,
    None is returned.

    :param db: Database session to be used for creating the client.
    :type db: Session
    :param payload: Dictionary containing additional client details.
    :type payload: dict
    :param name: Name of the client.
    :type name: str
    :param email: Email address of the client.
    :type email: str
    :param phone: Phone number of the client.
    :type phone: str
    :param company: Name of the company associated with the client.
    :type company: str
    :return: The created Client object if successful, or None otherwise.
    :rtype: Client | None
    """
    if payload["role"] != "commercial":
        print("Seul les commerciaux peuvent créer des clients.")
        return None

    commercial = db.query(Collaborator).filter_by(email=payload["sub"]).first()
    if not commercial:
        print("Collaborateur non trouvé.")
        return None

    client = Client(
        name=name,
        email=email,
        phone=phone,
        company=company,
        creation_date=date.today(),
        commercial_id=commercial.id
    )

    db.add(client)
    db.commit()
    db.refresh(client)
    print("Client crée et associé au commercial")
    return client

def update_client(
        db: Session,
        payload: dict,
        client_id: int,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        company: str | None = None
) -> Client | None:
    """
    Update an existing client's information in the database. The function retrieves a
    specific client using the provided client ID, modifies its information with the
    given payload values or individual field updates, and saves the changes back to
    the database. Optionally, the client's name, email, phone, or company can be
    updated using additional arguments.

    :param db: Database session instance used to fetch and commit changes for
        the client.
    :param payload: Dictionary containing updated field values for the client.
    :param client_id: Unique identifier of the client to update.
    :param name: New name for the client, if provided.
    :param email: New email address for the client, if provided.
    :param phone: New phone number for the client, if provided.
    :param company: New company name for the client, if provided.
    :return: The updated Client object if successful, otherwise None.
    """

    if payload["role"] != "commercial":
        print("Seul les commerciaux peuvent modifier les clients.")
        return None

    current_user = db.query(Collaborator).filter_by(email=payload["sub"]).first()
    if not current_user:
        print("Utilisateur introuvable.")
        return None

    client = db.query(Client).filter_by(id=client_id).first()
    if not client:
        print("Client introuvable.")
        return None

    if client.commercial_id != current_user.id:
        print("Vous n'avez pas le droit de modifier ce client.")
        return None

    if name is not None:
        client.name = name
    if email is not None:
        client.email = email
    if phone is not None:
        client.phone = phone
    if company is not None:
        client.company = company

    db.commit()
    db.refresh(client)
    print("Client mis à jour")
    return client
