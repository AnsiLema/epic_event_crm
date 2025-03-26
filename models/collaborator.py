from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class Collaborator(Base):
    __tablename__ = "collaborators"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False) # exemple : 'commercial', 'support', 'management'

    clients = relationship("Client", back_populates="commercial") # 'commercial'
    contracts = relationship("Contract", back_populates="commercial") # 'commercial'
    events = relationship("Event", back_populates="support") # 'support'