from sqlalchemy.orm import Session
from models.collaborator import Collaborator
from security.password import verify_password

def authenticate_collaborator(
        db: Session,
        email: str,
        password: str,
) -> Collaborator | None:
    """
    Checks email and password to authenticate collaborators.
    Return the collaborator if valid, None otherwise.
    """
    user = db.query(Collaborator).filter_by(email=email).first()

    if not user:
        return None

    if not verify_password(password, str(user.password)):
        return None

    return user

if __name__ == "__main__":
    from db.session import SessionLocal
    session = SessionLocal()
    result = authenticate_collaborator(session, "alice@epicevents.fr", "supersecure123")
    print(f"Utilisateur : {result.name} ({result.email}) - Rôle : {result.role.name}")