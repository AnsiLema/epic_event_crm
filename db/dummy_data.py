from datetime import datetime, date
from session import SessionLocal
from models import Collaborator, Client, Contract, Event
from security.password import hash_password

session = SessionLocal()

# Créer un collaborateur commercial
commercial = Collaborator(
    name="Bill Boquet",
    email="bill@epic-events.com",
    password=hash_password("secret123"),
    role="commercial"
)

# Un support
support = Collaborator(
    name="Alice Support",
    email="alice@epic-events.com",
    password=hash_password("support456"),
    role="support"
)

# Un client
client = Client(
    name="Kevin Casey",
    email="kevin@startup.io",
    phone="+67812345678",
    company="Cool Startup LLC",
    creation_date=date(2021, 4, 18),
    last_contact_date=date(2023, 3, 29),
    commercial_id=commercial.id
)

# Un contrat
contract = Contract(
    total_amount=3000.00,
    amount_left=1000.00,
    creation_date=date.today(),
    status=True,
    client_id=client.id,
    commercial_id=commercial.id
)

# Un événement
event = Event(
    contract_id=contract.id,
    support_id=support.id,
    start_date=datetime(2024, 6, 4, 13, 0),
    end_date=datetime(2024, 6, 5, 2, 0),
    location="53 Rue du Château, Candé-sur-Beuvron",
    attendees=75,
    note="Organiser le DJ après le repas"
)

session.add_all([commercial, support, client, contract, event])
session.commit()
session.close()

print("✅ Données de test insérées avec succès.")