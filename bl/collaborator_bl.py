from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dal.collaborator_dal import CollaboratorDAL
from dal.role_dal import RoleDAL
from security.permissions import can_manage_collaborators
from dtos.collaborator_dto import CollaboratorDTO


class CollaboratorBL:
    def __init__(self, db: Session):
        self.db = db
        self.dal = CollaboratorDAL(db)

    def create_collaborator(self, data: dict, current_user: dict) -> CollaboratorDTO:
        if not can_manage_collaborators(current_user):
            raise PermissionError("Vous n'avez pas le droit de créer un collaborateur")
        return self.dal.create(data)

    def create_collaborator_from_input(self,
                                       name: str,
                                        email: str,
                                        password: str,
                                        role_name: str,
                                        current_user: dict) -> CollaboratorDTO:
        if not can_manage_collaborators(current_user):
            raise PermissionError("Vous n'avez pas le droit de créer un collaborateur")

        if not name or not email or not password or not role_name:
            raise ValueError("Tous les champs sont requis")

        if len(password) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")

        if self.dal.get_by_email_raw(email):
            raise ValueError("Un collaborateur avec cet email existe déjà.")

        role_dal = RoleDAL(self.db)
        role = role_dal.get_raw_by_name(role_name)
        if not role:
            raise ValueError(f"Le role '{role_name}' n'existe pas.")

        try:
            collaborator_data = {
                "name": name,
                "email": email,
                "password": password,
                "role_id": role.id
            }
            return self.dal.create(collaborator_data)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Erreur: Cet email est déjà utilisé.")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Une erreur inattendue est survenue : {e}")

    def update_collaborator(self, collaborator_id: int, updates: dict, current_user: dict) -> CollaboratorDTO:
        if not can_manage_collaborators(current_user):
            raise PermissionError("Vous n'avez pas le droit de modifier un collaborateur")
        updated_collaborator = self.dal.update_by_id(collaborator_id, updates)
        if not updated_collaborator:
            raise ValueError("collaborateur introuvable")
        return updated_collaborator

    def delete_collaborator(self, collaborator_id: int, current_user: dict) -> None:
        if not can_manage_collaborators(current_user):
            raise PermissionError("Vous n'avez pas le droit de supprimer un collaborateur")
        success = self.dal.delete_by_id(collaborator_id)
        if not success:
            raise ValueError("collaborateur introuvable")