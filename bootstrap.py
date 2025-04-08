from sqlalchemy.orm import sessionmaker
from db.session import engine
from models.role import Role
from models.collaborator import Collaborator
from security.password import hash_password


Session = sessionmaker(bind=engine)
db = Session()

def init_roles():
    existing_roles = db.query(Role).all()
    if existing_roles:
        print("Rôles déjà existants.")
        return

    for role_name in ["gestion", "commercial", "support"]:
        db.add(Role(name=role_name))
    db.commit()
    print("Rôles créés avec succès.")

def init_admin_user():
    admin_email = "admin@epicevents.fr"
    admin = db.query(Collaborator).filter_by(email=admin_email).first()

    if admin:
        print("Administrateur déja existant.")
        return

    gestion_role = db.query(Role).filter_by(name="gestion").first()
    if not gestion_role:
        print("Rôle 'gestion' introuvable. Initialisation intérrompue.")
        return

    password = hash_password("admin123")
    admin_user = Collaborator(
        name="Admin",
        email=admin_email,
        password=password,
        role_id=gestion_role.id
    )
    db.add(admin_user)
    db.commit()
    print("Collaborateur admin créé : admin@epicevents.fr / admin123")

if __name__ == "__main__":
    print("Initialisation de l'application...")
    init_roles()
    init_admin_user()
    print("Initialisation terminée.")