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