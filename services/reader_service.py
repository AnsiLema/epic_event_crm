from sqlalchemy.orm import Session
from models.client import Client
from models.event import Event
from models.contract import Contract


def get_all_clients(db: Session) -> list[Client]:
    return db.query(Client).all()

def get_all_events(db: Session) -> list[Event]:
    return db.query(Event).all()

def get_all_contracts(db: Session) -> list[Contract]:
    return db.query(Contract).all()