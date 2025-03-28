from db.session import SessionLocal
from security.token_store import load_token
from security.jwt import decode_access_token
from services.collaborator_service import update_collaborator

session = SessionLocal()

token = load_token()
if not token:
    print("❌ Vous devez vous connecter.")
    exit()

payload = decode_access_token(token)
if not payload:
    print("❌ Token invalide ou expiré.")
    exit()

# Test manuel : update du collaborateur #1
updated = update_collaborator(
    db=session,
    payload=payload,
    collaborator_id=1,
    new_name="Alice M.",
    new_email="alice.updated@epicevents.fr",
    new_password="newpass123",
    new_role_name="support"
)

if updated:
    print(f"👍 Nouveau nom : {updated.name}, email : {updated.email}, rôle : {updated.role.name}")

session.close()