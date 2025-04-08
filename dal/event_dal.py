from sqlalchemy.orm import Session
from models.event import Event
from dtos.event_dto import EventDTO


class EventDAL:
    def __init__(self, db: Session):
        self.db = db

    def _to_dto(self, event: Event) -> EventDTO:
        return EventDTO(
            id=event.id,
            start_date=event.start_date,
            end_date=event.end_date,
            location=event.location,
            attendees=event.attendees,
            note=event.note,
            contract_id=event.contract_id,
            support_id=event.support_id
        )

    def get(self, event_id: int) -> EventDTO | None:
        event = self.db.query(Event).filter_by(id=event_id).first()
        if not event:
            return None
        return self._to_dto(event)

    def create(self, data: dict) -> EventDTO:
        event = Event(**data)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return self._to_dto(event)

    def update(self, event: Event, updates: dict) -> EventDTO:
        for key, value in updates.items():
            setattr(event, key, value)
        self.db.commit()
        self.db.refresh(event)
        return self._to_dto(event)

    def update_by_id(self, event_id: int, updates: dict) -> EventDTO | None:
        event = self.db.query(Event).filter_by(id=event_id).first()
        if not event:
            return None
        return self.update(event, updates)

    def get_all(self) -> list[EventDTO]:
        events = self.db.query(Event).all()
        return [self._to_dto(e) for e in events]

    def get_without_support(self) -> list[EventDTO]:
        events = self.db.query(Event).filter_by(support_id=None).all()
        return [self._to_dto(e) for e in events]

    def get_by_support_id(self, support_id: int) -> list[EventDTO]:
        events = self.db.query(Event).filter_by(support_id=support_id).all()
        return [self._to_dto(e) for e in events]