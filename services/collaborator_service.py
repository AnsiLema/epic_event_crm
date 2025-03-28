from typing import Type
from sqlalchemy.orm import Session
from models import Collaborator
from models.collaborator import Collaborator
from models.role import Role
from security.password import hash_password
from security.permissions import can_manage_collaborators

def update_collaborator(
        db: Session,
        payload: dict,
        collaborator_id: int,
        new_name: str | None = None,
        new_email: str | None = None,
        new_password: str | None = None,
        new_role_name: str | None = None
) -> Type[Collaborator] | None:
    """
    Updates the details of an existing collaborator in the database with
    specified new values. Only provided fields are updated, keeping the
    others unchanged. If the collaborator does not exist or no updates
    are performed, the function may return None. This operation ensures
    that the new collaborator information is persisted in the database.
    Only contributor with role "gestion" can update collaborators.

    :param db: Database session used to perform the update operations.
    :type db: Session
    :param payload: Dictionary containing additional data needed for the update.
    :type payload: dict
    :param collaborator_id: ID of the collaborator whose details will be updated.
    :type collaborator_id: int
    :param new_name: New name to update for the collaborator. Defaults to None if not provided.
    :type new_name: str | None
    :param new_email: New email to update for the collaborator. Defaults to None if not provided.
    :type new_email: str | None
    :param new_password: New password to update for the collaborator. Defaults to None if not provided.
    :type new_password: str | None
    :param new_role_name: New role name to update for the collaborator. Defaults to None if not provided.
    :type new_role_name: str | None
    :return: The updated collaborator object if the update is successful, otherwise None.
    :rtype: Collaborator | None
    """
    if not can_manage_collaborators(payload):
        print("Permission refusée : Seuls les gestionnaires ont le droit de modifier les collaborateurs.")
        return None

    collaborator = db.query(Collaborator).filter_by(id=collaborator_id).first()
    if not collaborator:
        print("Collaborateur introuvable.")
        return None

    if new_name:
        collaborator.name = new_name
    if new_email:
        collaborator.email = new_email
    if new_password:
        hashed_pw = hash_password(new_password)
        collaborator.password = hashed_pw
    if new_role_name:
        role = db.query(Role).filter_by(name=new_role_name).first()
        if not role:
            print("Role demandé inexistant.")
            return None
        collaborator.role = role

    db.commit()
    db.refresh(collaborator)
    print("Collaborateur mis à jour avec succès.")
    return collaborator