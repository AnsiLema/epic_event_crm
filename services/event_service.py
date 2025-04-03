from sqlalchemy.orm import Session
from datetime import datetime

from models.event import Event
from models.contract import Contract
from models.collaborator import Collaborator
from security.permissions import is_commercial


def create_event(
        db: Session,
        payload: dict,
        contract_id: int,
        start_date: datetime,
        end_date: datetime,
        location: str,
        attendees: str,
        note: str = ""
) -> Event | None:
    """
    Creates a new event and stores it in the database. This function is used to associate
    an event with a specific contract ID, along with details such as start and end times,
    location, attendees, and additional notes. If the operation is successful, it returns
    the created event object. Otherwise, it returns None.

    :param db: Database session used for the operation
    :type db: Session
    :param payload: Dictionary containing event-related data for processing
    :type payload: dict
    :param contract_id: ID of the contract associated with the event
    :param start_date: Start datetime of the event
    :type start_date: datetime
    :param end_date: End datetime of the event
    :type end_date: datetime
    :param location: Location where the event will take place
    :type location: str
    :param attendees: List or details of attendees for the event
    :type attendees: str
    :param note: Optional additional notes about the event
    :type note: str, optional
    :return: The created event if successful, or None if the operation fails
    :rtype: Event | None
    """

    if not is_commercial(payload):
        print("Seul les commerciaux peuvent créer un évènement.")
        return None

    commercial = db.query(Collaborator).filter_by(email=payload["sub"]).first()
    if not commercial:
        print("Collaborateur introuvable.")
        return None

    contract = db.query(Contract).filter_by(id=contract_id).first()
    if not contract:
        print("Contract introuvable.")
        return None

    if not contract.status:
        print("Ce contrat n'est pas encore signé.")
        return None

    if contract.client.commercial_id != commercial.id:
        print("Vous n'êtes pas le commercial responsable de ce client.")
        return None

    event = Event(
        start_date=start_date,
        end_date=end_date,
        location=location,
        attendees=attendees,
        note=note,
        contract=contract,
        support=None
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    print(f" Évènement #{event.id} créé pour le contrat #{contract.id}.")
    return event