from dataclasses import dataclass
from datetime import date


@dataclass
class ContractDTO:
    id: int
    total_amount: float
    amount_left: float
    creation_date: date
    status: bool
    client_id: int
    commercial_id: int

