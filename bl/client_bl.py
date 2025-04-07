from sqlalchemy.orm import Session
from dal.client_dal import ClientDAL
from models.collaborator import Collaborator
from security.permissions import is_commercial
from datetime import date
from dtos.client_dto import ClientDTO


class ClientBLL:
    def __init__(self, db: Session):
        self.db = db
        self.dal = ClientDAL(db)

    def create_client(self, data: dict, current_user: dict) -> ClientDTO:
        if not is_commercial(current_user):
            raise PermissionError("Seuls les commerciaux peuvent créer un client")
        collaborator = self.db.query(Collaborator).filter_by(email=current_user["sub"]).first()
        if not collaborator:
            raise ValueError("collaborateur introuvable")

        data["commercial_id"] = collaborator.id
        data["creation_date"] = date.today()

        return self.dal.create(data)

    def update_client(self, client_id: int, updates: dict, current_user: dict) -> ClientDTO:
        if not is_commercial(current_user):
            raise PermissionError("Seuls les commerciaux peuvent modifier un client")

        collaborator = self.db.query(Collaborator).filter_by(email=current_user["sub"]).first()
        if not collaborator:
            raise ValueError("collaborateur introuvable")

        client = self.dal.get(client_id)
        if not client:
            raise ValueError("client introuvable")

        if client.commercial_id != collaborator.id:
            raise PermissionError("Vous ne pouvez modifier que vos propres clients.")

        return self.dal.update_by_id(client_id, updates)

    def get_client(self, client_id: int) -> ClientDTO:
        client = self.dal.get(client_id)
        if not client:
            raise ValueError("client introuvable")
        return client
