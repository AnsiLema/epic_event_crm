from sqlalchemy.orm import Session
from models.collaborator import Collaborator
from security.password import hash_password

def create_collaborator(
        db: Session,
        id: str,
        name: str,
        email: str,
        password: str,
        role: str
) -> Collaborator:
    hashed_password = hash_password(password)

    user = Collaborator(

    )