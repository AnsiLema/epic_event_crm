from sqlalchemy.orm import Session

from models import Collaborator
from models.client import Client
from models.event import Event
from models.contract import Contract


def get_all_clients(db: Session) -> list[Client]:
    return db.query(Client).all()

def get_all_events(db: Session) -> list[Event]:
    return db.query(Event).all()

def get_all_contracts(db: Session) -> list[Contract]:
    return db.query(Contract).all()

def get_clients_by_commercial(db: Session, commercial_email: str):
    return db.query(Client).join(Collaborator).filter(Collaborator.email == commercial_email).all()

def get_contracts_not_signed(db: Session):
    return db.query(Contract).filter_by(status=False).all()

def get_contracts_not_fully_paid(db: Session):
    return db.query(Contract).filter_by(Contract.amount_left > 0).all()

def get_events_without_support(db: Session):
    return db.query(Event).filter_by(support_id=None).all()

def get_events_by_support(db: Session, support_email: str):
    return db.query(Event).join(Collaborator).filter(Collaborator.email == support_email).all()