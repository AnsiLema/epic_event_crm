from db.session import SessionLocal
from services.user_service import create_collaborator
from models.role import Role

db = SessionLocal()

# Créer les rôles s'ils n'existent pas encore
for name in ["commercial", "support", "gestion"]:
    if not db.query(Role).filter_by(name=name).first():
        db.add(Role(name=name))
db.commit()

# Créer un collaborateur
user = create_collaborator(
    db=db,
    name="Gilbert Commercial",
    email="gilbert@epicevents.fr",
    password="supersecure123",
    role_name="commercial"
)

if user:
    print(f"✅ Utilisateur créé : {user.name} - Rôle : {user.role.name}")
else:
    print("❌ Échec de la création")

db.close()