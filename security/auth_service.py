from dal.collaborator_dal import CollaboratorDAL
from security.password import verify_password

def authenticate_collaborator(db, email: str, password: str) -> dict | None:
    """
    Authenticates a collaborator by verifying the provided email and password.
    If the credentials are valid, the collaborator's essential information is
    returned as a dictionary.

    :param db: Database session or connection object used for querying.
    :type db: Any
    :param email: The email address of the collaborator to authenticate.
    :param password: The plain text password to verify against the stored hash.
    :return: A dictionary containing the collaborator's `id`, `email`, and `role`
        if authentication is successful, otherwise `None`.
    :rtype: dict | None
    """
    dal = CollaboratorDAL(db)
    user = dal.get_by_email_raw(email)

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return {
        "id": user.id,
        "sub": user.email,
        "email": user.email,
        "role": user.role.name
    }
