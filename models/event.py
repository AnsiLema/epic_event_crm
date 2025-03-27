from sqlalchemy import Column, Integer, String, ForeignKey,Text, DateTime
from sqlalchemy.orm import relationship
from .base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String)
    attendees = Column(Integer)
    note = Column(Text)

    contract_id = Column(Integer, ForeignKey("contracts.id"))
    contract = relationship("Contract", back_populates="event")

    support_id = Column(Integer, ForeignKey("collaborators.id"))
    support = relationship("Collaborator", back_populates="events")