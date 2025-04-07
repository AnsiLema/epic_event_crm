from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class EventDTO:
    id: int
    start_date: datetime
    end_date: datetime
    location: str
    attendees: int
    note: Optional[str]
    contract_id: int
    support_id: Optional[int]