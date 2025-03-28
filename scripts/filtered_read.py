from db.session import SessionLocal
from security.token_store import load_token
from security.jwt import decode_access_token
from services.reader_service import (
    get_clients_by_commercial,
    get_contracts_not_signed,
    get_contracts_not_fully_paid,
    get_events_without_support,
    get_events_by_support
)

token = load_token()
if not token:
    print("❌ Vous devez d'abord vous connecter.")
    exit()

payload = decode_access_token(token)
if not payload:
    print("❌ Token invalide ou expiré.")
    exit()

role = payload["role"]
email = payload["sub"]

session = SessionLocal()

print(f"🔍 Lecture filtrée pour le rôle : {role}\n")

if role == "gestion":
    print("📌 Événements sans support :")
    for e in get_events_without_support(session):
        print(f"- Event #{e.id} à {e.location} (contrat #{e.contract_id})")

elif role == "commercial":
    print("📌 Clients associés à vous :")
    for c in get_clients_by_commercial(session, email):
        print(f"- {c.name} ({c.email})")

    print("\n📌 Contrats non signés :")
    for c in get_contracts_not_signed(session):
        print(f"- Contrat #{c.id}, client #{c.client_id}")

    print("\n📌 Contrats non totalement payés :")
    for c in get_contracts_not_fully_paid(session):
        print(f"- Contrat #{c.id}, reste dû : {c.amount_left}")

elif role == "support":
    print("📌 Vos événements :")
    for e in get_events_by_support(session, email):
        print(f"- Event #{e.id}, à {e.location}")

else:
    print("ℹ️ Aucun filtre spécial pour ce rôle.")

session.close()