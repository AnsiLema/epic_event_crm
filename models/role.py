from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    collaborators = relationship("Collaborator", back_populates="role")

    def __repr__(self):
        return f"<Role(name={self.name})>"