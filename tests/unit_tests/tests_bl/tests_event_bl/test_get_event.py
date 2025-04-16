from datetime import datetime
from unittest.mock import MagicMock, create_autospec

import pytest
from bl.event_bl import EventBL
from dal.collaborator_dal import CollaboratorDAL
from dal.contract_dal import ContractDAL
from dal.event_dal import EventDAL
from dtos.event_dto import EventDTO
from security.permissions import is_commercial, can_manage_events, is_support
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    return create_autospec(Session)


@pytest.fixture
def event_bl(mock_db):
    return EventBL(mock_db)


@pytest.fixture
def mock_event_dto():
    return EventDTO(
        id=1,
        start_date=datetime(2023, 10, 1, 10, 0),
        end_date=datetime(2023, 10, 1, 12, 0),
        location="Conference Hall",
        attendees=100,
        note="Annual meeting",
        contract_id=1,
        support_id=None,
    )


def test_get_event_success(event_bl, mock_event_dto):
    event_bl.dal.get = MagicMock(return_value=mock_event_dto)
    event = event_bl.get_event(1)
    assert isinstance(event, EventDTO)
    assert event.id == mock_event_dto.id


def test_get_event_not_found(event_bl):
    event_bl.dal.get = MagicMock(return_value=None)
    with pytest.raises(ValueError, match="Évènement introuvable."):
        event_bl.get_event(999)