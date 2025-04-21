from sqlalchemy.orm import Session
from dal.role_dal import RoleDAL
from dtos.role_dto import RoleDTO


class RoleBL:
    def __init__(self, db: Session):
        self.dal = RoleDAL(db)

    def list_roles(self) -> list[RoleDTO]:
        return self.dal.get_all()

    def get_role_by_name(self, name: str) -> RoleDTO:
        role = self.dal.get_by_name(name)
        if not role:
            raise ValueError("Role introuvable.")
        return role

    def create_default_roles(self, name: str) -> bool:
        if not self.dal.get_by_name(name):
            for role in ["gestion", "commercial", "support"]:
                self.dal.create_role(role)
            return True
        return False

    def get_gestion_role(self):
        return self.dal.get_by_name("gestion")

    def create_role(self, name: str) -> RoleDTO:
        existing = self.dal.get_by_name(name)
        if existing:
            raise ValueError(f"Le role {name} existe déja.")
        return self.dal.create_role(name)

