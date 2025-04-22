from sqlalchemy.orm import Session
from models.collaborator import Collaborator
from dtos.collaborator_dto import CollaboratorDTO


class CollaboratorDAL:
    def __init__(self, db: Session):
        self.db = db

    def _to_dto(self, collaborator: Collaborator) -> CollaboratorDTO:
        return CollaboratorDTO(
            id=collaborator.id,
            name=collaborator.name,
            email=collaborator.email,
            role_name=collaborator.role.name
        )

    def get_by_id(self, collaborator_id: int) -> CollaboratorDTO | None:
        """
        Fetches a collaborator by their unique identifier.

        This method retrieves a collaborator record from the database based on the
        provided unique identifier. If a collaborator with the given ID exists,
        it converts the result into a data transfer object (DTO); otherwise,
        it returns None.

        :param collaborator_id: The unique identifier of the collaborator to fetch.
        :type collaborator_id: int
        :return: A data transfer object representing the collaborator if found,
            otherwise None.
        :rtype: CollaboratorDTO | None
        """
        collaborator = self.db.query(Collaborator).filter_by(id=collaborator_id).first()
        return self._to_dto(collaborator) if collaborator else None

    def get_by_email(self, email: str) -> CollaboratorDTO | None:
        """
        Retrieve a collaborator by their email address.

        This method attempts to locate a collaborator in the database using their
        email address. If a match is found, it converts the collaborator's data
        into a Data Transfer Object (DTO) and returns it. If no match is found,
        it returns None.

        :param email: The email address of the collaborator to retrieve.
        :type email: str
        :return: A CollaboratorDTO instance if a collaborator is found, otherwise None.
        :rtype: CollaboratorDTO | None
        """
        collaborator = self.db.query(Collaborator).filter_by(email=email).first()
        return self._to_dto(collaborator) if collaborator else None

    def get_by_email_raw(self, email: str) -> Collaborator | None:
        """
        Fetch a collaborator from the database by their email address.

        This function queries the database for a `Collaborator` instance based on
        the provided email address. If no collaborator with the given email address
        exists in the database, the function returns `None`.

        :param email: The email address of the collaborator to be retrieved.
        :type email: str
        :return: A `Collaborator` object if a match is found, otherwise `None`.
        :rtype: Collaborator | None
        """
        return self.db.query(Collaborator).filter_by(email=email).first()

    def get_all(self) -> list[CollaboratorDTO]:
        """
        Retrieves all collaborators from the database and transforms them
        into a list of CollaboratorDTO instances.

        This method queries the database for all instances of the `Collaborator`
        model class, maps each one into a `CollaboratorDTO`, and returns the
        list of these DTO objects.

        :return: A list of `CollaboratorDTO` objects representing all
            collaborators in the database.
        :rtype: list[CollaboratorDTO]
        """
        collaborators = self.db.query(Collaborator).all()
        return [self._to_dto(c) for c in collaborators]

    def create(self, data: dict) -> CollaboratorDTO:
        collaborator = Collaborator(**data)
        self.db.add(collaborator)
        self.db.commit()
        self.db.refresh(collaborator)
        return self._to_dto(collaborator)

    def update_by_id(self, collaborator_id: int, updates: dict) -> CollaboratorDTO | None:
        """
        Updates a collaborator's details in the database by their unique identifier. If the collaborator
        does not exist, the function will return None. The `updates` dictionary is used to dynamically
        update the collaborator's attributes specified by the dictionary's keys.

        :param collaborator_id: The unique identifier of the collaborator to be updated.
        :type collaborator_id: int
        :param updates: A dictionary containing the fields and their corresponding values to update
                        for the targeted collaborator.
        :type updates: dict
        :return: Returns an updated `CollaboratorDTO` object representing the updated collaborator.
                 If the collaborator is not found, returns None.
        :rtype: CollaboratorDTO | None
        """
        collaborator = self.db.query(Collaborator).filter_by(id=collaborator_id).first()
        if not collaborator:
            return None
        for key, value in updates.items():
            setattr(collaborator, key, value)
        self.db.commit()
        self.db.refresh(collaborator)
        return self._to_dto(collaborator)

    def delete_by_id(self, collaborator_id: int) -> bool:
        """
        Deletes a collaborator record from the database using the specified collaborator ID. If the collaborator
        with the specified ID does not exist in the database, the operation will return False. Otherwise, it will
        delete the record and commit the changes.

        :param collaborator_id: The ID of the collaborator to be deleted.
        :type collaborator_id: int
        :return: True if the collaborator was found and deleted successfully, False otherwise.
        :rtype: bool
        """
        collaborator = self.db.query(Collaborator).filter_by(id=collaborator_id).first()
        if not collaborator:
            return False
        self.db.delete(collaborator)
        self.db.commit()
        return True
