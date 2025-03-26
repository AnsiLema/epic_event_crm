from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    company = Column(String)
    creation_date = Column(Date)
    last_contact_date = Column(Date)

    commercial_id = Column(Integer, ForeignKey("collaborators.id"))
    commercial = relationship("Collaborator", back_populates="clients")

    contracts = relationship("Contract", back_populates="client")