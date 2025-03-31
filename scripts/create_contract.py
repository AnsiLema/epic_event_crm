from db.dummy_data import contract
from db.session import SessionLocal
from security.token_store import load_token
from security.jwt import decode_access_token
from services.contract_service import create_contract


session = SessionLocal()

token = load_token()
if not token:
    print("Vous devez d'abord vous connecter.")
    exit()

payload = decode_access_token(token)
if not payload:
    print("Token invalide ou expiré")
    exit()

# Exemple : create a contract from client #1
Contract = create_contract(
    db=session,
    payload=payload,
    client_id=1,
    total_amount=5000.00,
    amount_left=2500.00,
    is_signed=False
)

if contract:
    print(f"Contrat #{contract.id} créé pour le client #{contract.client_id}, avec {contract.commercial.name}.")
session.close()