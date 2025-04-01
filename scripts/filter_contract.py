from db.session import SessionLocal
from security.token_store import load_token
from security.jwt import decode_access_token
from services.contract_service import filter_contracts

session = SessionLocal()

token = load_token()
if not token:
    print("Connectez-vous d'abord.")
    exit()

payload = decode_access_token(token)
if not payload:
    print("Token invalide ou expiré.")
    exit()

# Choix du filtre : "unsigned" ou "unpaid"
filtered = filter_contracts(session, payload, filter_by="unpaid")

if not filtered:
    print("Aucun contrat correspondant trouvé.")  # Exemple de retour si aucun contrat n'est trouvé.
else:
    for contract in filtered:
        print(
            f"📄 Contrat #{contract.id} | Client : {contract.client.name} de {contract.client.company} | Montant total : {contract.total_amount} € | Restant : {contract.amount_left} € | Signé : {contract.status}")

session.close()
