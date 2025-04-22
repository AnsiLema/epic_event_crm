from sqlalchemy.orm import Session
from dal.event_dal import EventDAL
from dal.contract_dal import ContractDAL
from dal.collaborator_dal import CollaboratorDAL
from dtos.event_dto import EventDTO
from security.permissions import can_manage_events, is_commercial, is_support


class EventBL:
    def __init__(self, db: Session):
        self.dal = EventDAL(db)
        self.contract_dal = ContractDAL(db)
        self.collaborator_dal = CollaboratorDAL(db)

    def get_event(self, event_id: int) -> EventDTO:
        event = self.dal.get(event_id)
        if not event:
            raise ValueError("Évènement introuvable.")
        return event

    def list_all_events(self) -> list[EventDTO]:
        return self.dal.get_all()

    def create_event(self, event_data: dict, current_user: dict) -> EventDTO:
        if not is_commercial(current_user):
            raise PermissionError("Seuls les commerciaux peuvent créer un évènements")

        # Checks that the contract exists
        contract = self.contract_dal.get(event_data["contract_id"])
        if not contract:
            raise ValueError("Le contrat introuvable.")

        # Checks that contract is signed
        if not contract.status:
            raise PermissionError("Impossible de créer un évènement pour un contrat non signé.")

        # Checks that the collaborator manages the contract
        user = self.collaborator_dal.get_by_email_raw(current_user["sub"])
        if contract.commercial_id != user.id:
            raise PermissionError("Vous ne pouvez créer un évènement que pour vos propres contrats.")

        return self.dal.create(event_data)

    def update_event(self, event_id: int, updates: dict, current_user: dict) -> EventDTO:
        event = self.dal.get(event_id)
        if not event:
            raise ValueError("Évènement introuvable.")

        # Management can modify all events
        if can_manage_events(current_user):
            return self.dal.update_by_id(event_id, updates)

        # Support can update its own event
        if is_support(current_user):
            user = self.collaborator_dal.get_by_email_raw(current_user["sub"])
            if event.support_id != user.id:
                raise PermissionError("Vous ne pouvez modifier que les événements qui vous sont attribués.")
            return self.dal.update_by_id(event_id, updates)

        raise PermissionError("Vous n'avez pas les droits pour modifier cet évènement.")

    def list_events_without_support(self, current_user: dict) -> list[EventDTO]:
        if not can_manage_events(current_user):
            raise PermissionError("Seuls les gestionnaires peuvent acceder à cette fonction.")
        return self.dal.get_without_support()

    def list_events_for_current_support(self, current_user: dict) -> list[EventDTO]:
        if not is_support(current_user):
            raise PermissionError("Seuls les membres de l'équipe support peuvent voir leurs évènements.")

        user = self.collaborator_dal.get_by_email_raw(current_user["sub"])
        if not user:
            raise ValueError("Utilisateur introuvable.")
        return self.dal.get_by_support_id(user.id)
