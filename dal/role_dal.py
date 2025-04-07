from sqlalchemy.orm import Session
from models.role import Role
from dtos.role_dto import RoleDTO


class RoleDAL:
    def __init__(self, db: Session):
        self.db = db

    def _to_dto(self, role: Role) -> RoleDTO:
        return RoleDTO(
            id=role.id,
            name=role.name
        )

    def get_raw_by_name(self, name: str) -> Role | None:
        """
        Fetches a Role object from the database filtered by the given name.

        This method queries the database for a Role instance whose name matches
        the provided `name` parameter. If a matching Role exists, it returns the
        Role object. Otherwise, it returns None.

        :param name: The name of the Role to search for in the database.
        :type name: str
        :return: A Role object if found, otherwise None.
        :rtype: Role | None
        """
        return self.db.query(Role).filter_by(name=name).first()

    def get_all(self) -> list[RoleDTO]:
        """
        Retrieves all roles from the database and converts them to DTOs.

        This method queries the Role table in the database to fetch all entries,
        then converts each entry into a RoleDTO object for structured data
        representation. The conversion is handled by an internal method
        `_to_dto` which transforms the Role entities into their corresponding DTOs.

        :return: A list of RoleDTO objects representing all roles in the database.
        :rtype: list[RoleDTO]
        """
        roles = self.db.query(Role).all()
        return [self._to_dto(r) for r in roles]

    def get_by_id(self, role_id: int) -> RoleDTO | None:
        """
        Fetches a role by its identifier from the database and converts it into a DTO.

        :param role_id: The unique identifier of the role.
        :type role_id: int
        :return: A DTO of the role if found, otherwise None.
        :rtype: RoleDTO | None
        """
        role = self.db.query(Role).filter_by(id=role_id).first()
        return self._to_dto(role) if role else None

    def get_by_name(self, name: str) -> RoleDTO | None:
        role = self.db.query(Role).filter_by(name=name).first()
        return self._to_dto(role) if role else None

    def create(self, name: str) -> RoleDTO:
        role = Role(name=name)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return self._to_dto(role)