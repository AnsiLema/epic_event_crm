from sqlalchemy.orm import Session
from dal.contract_dal import ContractDAL
from security.permissions import can_manage_contracts, is_commercial
from dtos.contract_dto import ContractDTO


class ContractBL:
    def __init__(self, db: Session):
        self.dal = ContractDAL(db)

    def create_contract(self, contract_data: dict, current_user: dict) -> ContractDTO:
        if not can_manage_contracts(current_user):
            raise PermissionError("Vous n'avez pas les droits pour créer un contrat.")

        return self.dal.create(contract_data)

    def update_contract(self, contract_id: int, updates: dict, current_user: dict) -> ContractDTO:
        contract = self.dal.get(contract_id)
        if not contract:
            raise ValueError("Contrat introuvable.")

        if not can_manage_contracts(current_user):
            raise PermissionError("Vous n'avez pas les droits pour modifier ce contrat.")

        if is_commercial(current_user):
            if contract.commercial_id != current_user["id"]:
                raise PermissionError("Vous ne pouvez modifier que les contrats de vos clients.")

        return self.dal.update_by_id(contract_id, updates)

    def get_contract(self, contract_id: int) -> ContractDTO:
        contract = self.dal.get(contract_id)
        if not contract:
            raise ValueError("Contrat introuvable.")
        return contract

    def list_unsigned_contracts(self) -> list[ContractDTO]:
        return self.dal.filter_by_status(signed=False)

    def list_signed_contracts(self) -> list[ContractDTO]:
        return self.dal.filter_by_status(signed=True)

    def list_all_contracts(self) -> list[ContractDTO]:
        return self.dal.get_all()

