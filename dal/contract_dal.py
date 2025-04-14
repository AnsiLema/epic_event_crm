from sqlalchemy.orm import Session
from models.contract import Contract
from dtos.contract_dto import ContractDTO


class ContractDAL:
    def __init__(self, db: Session):
        self.db = db

    def _to_dto(self, contract: Contract) -> ContractDTO:
        return ContractDTO(
            id=contract.id,
            total_amount=contract.total_amount,
            amount_left=contract.amount_left,
            creation_date=contract.creation_date,
            status=contract.status,
            client_id=contract.client_id,
            commercial_id=contract.commercial_id
        )

    def get(self, contract_id: int) -> ContractDTO | None:
        contract = self.db.query(Contract).filter_by(id=contract_id).first()
        if not contract:
            return None
        return self._to_dto(contract)

    def create(self, data: dict) -> ContractDTO:
        contract = Contract(**data)
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return self._to_dto(contract)

    def update(self, contract_id: int, updates: dict) -> ContractDTO:
        contract = self.db.query(Contract).filter_by(id=contract_id).first()
        if not contract:
            return None
        for key, value in updates.items():
            setattr(contract, key, value)
        self.db.commit()
        self.db.refresh(contract)
        return self._to_dto(contract)

    def update_by_id(self, contract_id: int, updates: dict) -> ContractDTO | None:
        contract = self.db.query(Contract).filter_by(id=contract_id).first()
        if not contract:
            return None
        return self.update(contract_id, updates)

    def filter_by_status(self, signed: bool = True) -> list[ContractDTO]:
        contracts = self.db.query(Contract).filter_by(status=signed).all()
        return [self._to_dto(c) for c in contracts]

    def get_all(self) -> list[ContractDTO]:
        contracts = self.db.query(Contract).all()
        return [self._to_dto(c) for c in contracts]

