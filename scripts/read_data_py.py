from db.session import SessionLocal
from security.token_store import load_token
from security.jwt import decode_access_token
from services.reader_service import get_all_events, get_all_clients, get_all_contracts

token = load_token()
if not token:
    print("Vous devez d'bord vous connecter.")
    exit()

payload = decode_access_token(token)
if not payload:
    print("Token invalide ou expiré")
    exit()

session = SessionLocal()
print("Clients:")
for clients in get_all_clients(session):
    print(f"  - {clients.name} ({clients.email})")

print("\n Contrats :")
for contracts in get_all_contracts(session):
    print(f" - Contrat #{contracts.id}, "
          f"Total : {contracts.total_amount}, Statut : {'signé' if contracts.status else 'En attente'}")

print("\n Évènements :")
for event in get_all_events(session):
    print(f" - Évènement #{event.id}, lieu : {event.location}, participants : {event.attendees}")

session.close()
