from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, Boolean
from sqlalchemy.orm import relationship
from .base import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    total_amount = Column(Numeric, nullable=False)
    amount_left = Column(Numeric, nullable=False)
    creation_date = Column(Date, nullable=False)
    status = Column(Boolean, default=False)  # Signed or not

    client_id = Column(Integer, ForeignKey("clients.id"))
    commercial_id = Column(Integer, ForeignKey("collaborators.id"))

    client = relationship("Client", back_populates="contracts")
    commercial = relationship("Collaborator", back_populates="contracts")
    event = relationship("Event", back_populates="contract", uselist=False)
