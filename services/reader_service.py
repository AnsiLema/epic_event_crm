from sqlalchemy.orm import Session

from models import Collaborator
from models.client import Client
from models.event import Event
from models.contract import Contract


def get_all_clients(db: Session) -> list[Client]:
    """
    Retrieves all client records from the database.

    This function queries the database to fetch and return a list of all
    client records available. Each record corresponds to a Client object.
    """
    return db.query(Client).all()

def get_all_events(db: Session) -> list[Event]:
    """
    Retrieves all event records from the database.

    This function queries the database using the provided session to retrieve all
    records of events stored in the `Event` table. The results are returned as
    a list of event objects.
    """
    return db.query(Event).all()

def get_all_contracts(db: Session) -> list[Contract]:
    """
    Fetches all contracts from the database.

    This function retrieves all the records from the `Contract`
    table of the database passed via the session. It uses the
    SQLAlchemy query mechanism to fetch the data.
    """
    return db.query(Contract).all()

def get_clients_by_commercial(db: Session, commercial_email: str):
    """
    Retrieve a list of clients associated with a specific commercial.

    This function queries the database to find all clients linked to a collaborator
    (commercial) with the given email address. The operation joins the Client and
    Collaborator tables and filters by the provided email.
    """
    return db.query(Client).join(Collaborator).filter(Collaborator.email == commercial_email).all()

def get_contracts_not_signed(db: Session):
    """
    Fetches all contracts that have not been signed yet from the database.

    This function queries the `Contract` records in the database where the
    `status` field is set to `False`, indicating that the contract has not
    been signed. It retrieves all such records and returns them as a list.
    """
    return db.query(Contract).filter_by(status=False).all()

def get_contracts_not_fully_paid(db: Session):
    return db.query(Contract).filter(Contract.amount_left > 0, Contract.status == True).all()

def get_events_without_support(db: Session):
    return db.query(Event).filter_by(support_id=None).all()

def get_events_by_support(db: Session, support_email: str):
    return db.query(Event).join(Collaborator).filter(Collaborator.email == support_email).all()