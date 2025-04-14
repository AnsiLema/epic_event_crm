from sqlite3 import IntegrityError

from sqlalchemy.orm import Session
from dal.client_dal import ClientDAL
from dal.collaborator_dal import CollaboratorDAL
from models.collaborator import Collaborator
from security.permissions import is_commercial
from datetime import date
from dtos.client_dto import ClientDTO


class ClientBLL:
    def __init__(self, db: Session):
        self.db = db
        self.dal = ClientDAL(db)
        self.collaborator_dal = CollaboratorDAL(db)

    def create_client(self, data: dict, current_user: dict) -> ClientDTO:
        if not is_commercial(current_user):
            raise PermissionError("Seuls les commerciaux peuvent créer un client")
        collaborator = self.db.query(Collaborator).filter_by(email=current_user["sub"]).first()
        if not collaborator:
            raise ValueError("collaborateur introuvable")

        data["commercial_id"] = collaborator.id
        data["creation_date"] = date.today()

        return self.dal.create(data)

    def create_client_from_input(self, name: str,
                                 email: str,
                                 phone: str,
                                 company: str,
                                 current_user: dict) -> ClientDTO:
        if not is_commercial(current_user):
            raise PermissionError("Seuls les commerciaux peuvent créer des clients")

        if not name or not email:
            raise ValueError("Le nom et l'email sont requis.")

        if self.dal.get_by_email(email):
            raise ValueError ("Un client avec cet email existe déjà.")

        commercial = self.collaborator_dal.get_by_email_raw(current_user["sub"])
        if not commercial:
            raise ValueError("collaborateur introuvable")

        try:
            client_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "company": company,
                "commercial_id": commercial.id,
                "creation_date": date.today()
            }
            return self.dal.create(client_data)

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Email client déja utilisé.")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Une erreur inattendue est survenue : {e}")

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
