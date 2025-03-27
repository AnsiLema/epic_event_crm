from db.session import SessionLocal
from services.auth_service import authenticate_collaborator

session = SessionLocal()

email = input("Email: ")
password = input("Password: ")

user = authenticate_collaborator(session, email, password)

if user:
    print(f"Bienvenue {user.name} du département {user.role.name}.")
else:
    print("Email ou mot de passe incorrect.")


session.close()