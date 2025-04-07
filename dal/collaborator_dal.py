from sqlalchemy.orm import Session
from models.collaborator import Collaborator
from dtos.collaborator_dto import CollaboratorDTO


class CollaboratorDAL:
    def __init__(self, db: Session):
        self.db = db

    def _dto_to(self, collaborator: Collaborator) -> CollaboratorDTO:
        return CollaboratorDTO(
            id=collaborator.id,
            name=collaborator.name,
            email=collaborator.email,
            role_name=collaborator.role.name
        )

    def get_by_id(self, collaborator_id: int) -> CollaboratorDTO | None:
        collaborator = self.db.query(Collaborator).filter_by(id=collaborator_id).first()
        return self._to_dto(collaborator) if collaborator else None

    def get_by_email(self, email: str) -> CollaboratorDTO | None:
        collaborator = self.db.query(Collaborator).filter_by(email=email).first()
        return self._to_dto(collaborator) if collaborator else None

    def get_by_email_raw(self, email: str) -> Collaborator | None:
        return self.db.query(Collaborator).filter_by(email=email).first()

    def get_all(self) -> list[CollaboratorDTO]:
        collaborators = self.db.query(Collaborator).all()
        return [self._to_dto(c) for c in collaborators]

    def create(self, data: dict) -> CollaboratorDTO:
        collaborator = Collaborator(**data)
        self.db.add(collaborator)
        self.db.commit()
        self.db.refresh(collaborator)
        return self._to_dto(collaborator)

    def update_by_id(self, collaborator_id: int, updates: dict) -> CollaboratorDTO | None:
        collaborator = self.db.query(Collaborator).filter_by(id=collaborator_id).first()
        if not collaborator:
            return None
        for key, value in updates.items():
            setattr(collaborator, key, value)
        self.db.commit()
        self.db.refresh(collaborator)
        return self._to_dto(collaborator)

    def delete_by_id(self, collaborator_id: int) -> bool:
        collaborator = self.db.query(Collaborator).filter_by(id=collaborator_id).first()
        if not collaborator:
            return False
        self.db.delete(collaborator)
        self.db.commit()
        return True