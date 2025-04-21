from sqlalchemy.orm import Session
from dal.contract_dal import ContractDAL
from security.permissions import can_manage_contracts, is_commercial
from dtos.contract_dto import ContractDTO
from sentry_sdk import capture_message, set_user


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

        # logging before update
        status_before = contract.status
        status_after = updates.get("status", status_before)

        updated_contract = self.dal.update_by_id(contract_id, updates)

        # If contract was signed
        if not status_before and status_after:
            set_user({"email": current_user["email"]})
            capture_message(f"Contrat #{contract_id} signé par {current_user['email']}", level="info")

        return updated_contract


    def get_contract(self, contract_id: int) -> ContractDTO:
        contract = self.dal.get(contract_id)
        if not contract:
            raise ValueError("Contrat introuvable.")
        return contract

    def list_unsigned_contracts(self, current_user: dict) -> list[ContractDTO]:
        if not is_commercial(current_user):
            raise PermissionError("Seuls les commerciaux peuvent filtrer les contrats.")
        return self.dal.filter_by_status(signed=False)

    def list_signed_contracts(self, current_user: dict) -> list[ContractDTO]:
        if not is_commercial(current_user):
            raise PermissionError("Seuls les commerciaux peuvent filtrer les contrats.")
        return self.dal.filter_by_status(signed=True)

    def list_unpaid_contract(self, current_user: dict) -> list[ContractDTO]:
        if not is_commercial(current_user):
            raise PermissionError("Seuls les commerciaux peuvent filtrer les contrats.")
        return [c for c in self.dal.get_all() if c.amount_left > 0]

    def list_all_contracts(self) -> list[ContractDTO]:
        return self.dal.get_all()

