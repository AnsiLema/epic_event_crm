from db.session import SessionLocal
from security.token_store import save_token
from security.auth_service import authenticate_collaborator
from security.jwt import create_access_token

session = SessionLocal()

email = input("Email: ")
password = input("Password: ")

user = authenticate_collaborator(session, email, password)

if user:
    print(f"Bienvenue {user.name} du département {user.role.name}.")
    access_token = create_access_token({
        "sub": user.email,
        "role": user.role.name
    })
    print(f"🔐 Authentification réussie")
    save_token(access_token)
    print("Jeton sauvegardé localement")
else:
    print("Email ou mot de passe incorrect.")


session.close()