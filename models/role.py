from sqlalchemy import Column, Integer, String, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    collaborators = relationship("Collaborator", back_populates="role")

    __table_args__ = (
        CheckConstraint(
            "name IN('gestion', 'support', 'commercial')",
            name="check_role_name"
        ),
    )
