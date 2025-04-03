from datetime import datetime
from db.session import SessionLocal
from security.token_store import load_token
from security.jwt import decode_access_token
from services.event_service import create_event


session = SessionLocal()

token = load_token()
if not token:
    print("Vous devez d'abord vous connecter.")
    exit()

payload = decode_access_token(token)
if not payload:
    print("Jeton invalide ou expiré.")
    exit()

# Input data
try:
    contract_id = int(input("ID du contrat signé : "))

    start_str = input(" Date et heure de début (format : YYYY-MM-DD HH:MM) : ")
    end_str = input(" Date et heure de fin (format : YYYY-MM-DD HH:MM) : ")

    start_date = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
    end_date = datetime.strptime(end_str, "%Y-%m-%d %H:%M")

    location = input("Lieu : ")
    attendees = input("Nombre de participants : ")
    note = input("Notes (Facultatif) : ")

except Exception as e:
    print(f" Erreur de saisie : {e}")
    exit()

event = create_event(
    db=session,
    payload=payload,
    contract_id=contract_id,
    start_date=start_date,
    end_date=end_date,
    location=location,
    attendees=attendees,
    note=note
)

if event:
    print(f" Évènement #{event.id} créé avec succès.")
else:
    print(" Échec de la création de l'évènement.")

session.close()