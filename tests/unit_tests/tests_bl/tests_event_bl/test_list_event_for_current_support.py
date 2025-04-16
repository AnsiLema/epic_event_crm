from unittest.mock import patch, MagicMock

import pytest
from bl.event_bl import EventBL
from dtos.event_dto import EventDTO
from sqlalchemy.orm import Session


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_current_user_support():
    return {"sub": "support_user@test.com", "role": "support"}


@pytest.fixture
def mock_current_user_non_support():
    return {"sub": "unauthorized_user@test.com", "role": "commercial"}


@pytest.fixture
def mock_events_data():
    return [
        EventDTO(
            id=1,
            start_date="2023-01-01T10:00:00",
            end_date="2023-01-01T12:00:00",
            location="Location A",
            attendees=100,
            note="Meeting A",
            contract_id=5,
            support_id=10,
        ),
        EventDTO(
            id=2,
            start_date="2023-01-05T14:00:00",
            end_date="2023-01-05T16:00:00",
            location="Location B",
            attendees=50,
            note="Meeting B",
            contract_id=8,
            support_id=10,
        ),
    ]


@patch("bl.event_bl.CollaboratorDAL")
@patch("bl.event_bl.EventDAL")
def test_list_events_for_current_support_valid_user(
        mock_event_dal, mock_collaborator_dal, db_session, mock_current_user_support, mock_events_data
):
    """Test retrieving events for a current support user."""
    mock_collaborator_dal.return_value.get_by_email_raw.return_value = MagicMock(id=10)
    mock_event_dal.return_value.get_by_support_id.return_value = mock_events_data
    event_bl = EventBL(db_session)

    events = event_bl.list_events_for_current_support(mock_current_user_support)

    mock_collaborator_dal.return_value.get_by_email_raw.assert_called_once_with(mock_current_user_support["sub"])
    mock_event_dal.return_value.get_by_support_id.assert_called_once_with(10)
    assert events == mock_events_data


@patch("bl.event_bl.CollaboratorDAL")
def test_list_events_for_current_support_non_support_user(
        mock_collaborator_dal, db_session, mock_current_user_non_support
):
    """Test handling of a non-support user trying to access support events."""
    event_bl = EventBL(db_session)

    with pytest.raises(PermissionError, match="Seuls les membres de l'équipe support peuvent voir leurs évènements."):
        event_bl.list_events_for_current_support(mock_current_user_non_support)

    mock_collaborator_dal.return_value.get_by_email_raw.assert_not_called()


@patch("bl.event_bl.CollaboratorDAL")
def test_list_events_for_current_support_no_associated_user(
        mock_collaborator_dal, db_session, mock_current_user_support
):
    """Test handling when no collaborator is found for the current support user."""
    mock_collaborator_dal.return_value.get_by_email_raw.return_value = None
    event_bl = EventBL(db_session)

    with pytest.raises(ValueError, match="Utilisateur introuvable."):
        event_bl.list_events_for_current_support(mock_current_user_support)

    mock_collaborator_dal.return_value.get_by_email_raw.assert_called_once_with(mock_current_user_support["sub"])
