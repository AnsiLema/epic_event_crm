from security.token_store import load_token
from security.jwt import decode_access_token
from security.permissions import has_permission

token = load_token()

if not token:
    print("Aucun token trouvé; Veuillez vous connecter.")
    exit()

payload = decode_access_token(token)

if not payload:
    print("Token invalide ou expiré")
    exit()

if has_permission(payload, ["gestion", "commercial", "support"]):
    returnValue = True