from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class ClientDTO:
    id: int
    name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    creation_date: date
    last_contact_date: Optional[date]
    commercial_id: int
