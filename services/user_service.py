from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.collaborator import Collaborator
from security.password import hash_password
from models.role import Role


def create_collaborator(
    db: Session,
    name: str,
    email: str,
    password: str,
    role_name: str
) -> Collaborator | None:
    """
    Create a collaborator with a secure password and an existing role.
    Returns None if email already exists, or role does not exist.
    """
    # Validate entering data
    if not name or not email or not password or not role_name:
        print("⚠️ Tous les champs sont requis.")
        return None
    if len(password) < 8:
        print("⚠️ Le mot de passe doit contenir au moins 8 caractères")
        return None

    try:
        existing_user = db.query(Collaborator).filter_by(email=email).first()
        if existing_user:
            print("❌ Un collaborateur avec cet email existe déjà.")
            return None

        role = db.query(Role).filter_by(name=role_name).first()
        if not role:
            print(f"❌ Le rôle '{role_name}' n'existe pas.")
            return None

        # Password hashing
        hashed_pw = hash_password(password)

        # Collaborator creation
        user = Collaborator(
            name=name,
            email=email,
            password=hashed_pw,
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    except IntegrityError:
        db.rollback()
        print("⚠️ Conflit : un collaborateur avec cet email existe déjà.")
        return None
    except Exception as e:
        db.rollback()
        print(f"⚠️ Une erreur inattendue est survenue : {e}")
        return None

