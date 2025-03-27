from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Collaborator(Base):
    __tablename__ = "collaborators"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="collaborators")

    clients = relationship("Client", back_populates="commercial") # 'commercial'
    contracts = relationship("Contract", back_populates="commercial") # 'commercial'
    events = relationship("Event", back_populates="support") # 'support'