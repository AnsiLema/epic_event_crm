from db.session import SessionLocal
from security.token_store import load_token
from security.jwt import decode_access_token
from services.client_service import create_client

session = SessionLocal()

token = load_token()
if not token:
    print("Vous devez d'abord vous connecter.")
    exit()

payload = decode_access_token(token)
if not payload:
    print("Token invalide ou expiré.")
    exit()

client = create_client(
    db=session,
    payload=payload,
    name="Sophie Dubois",
    email="sophie.dubois@exemple.com",
    phone="0612131415",
    company="Dubois Conseil"
)

if client:
    print(f"Client #{client.id} : {client.name} ajouté avec succès.")

session.close()