from dataclasses import dataclass

@dataclass
class CollaboratorDTO:
    id: int
    name: str
    email: str
    role_name: str