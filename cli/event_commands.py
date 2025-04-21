import click
import sentry_sdk
from sqlalchemy.orm import sessionmaker
from bl.event_bl import EventBL
from cli.auth_decorator import with_auth_payload
from db.session import engine
from datetime import datetime

event_cli = click.Group("event")
Session = sessionmaker(bind=engine)

@event_cli.command("create")
@with_auth_payload
def create_event(current_user):
    """
    Creates a new event for the authenticated user.

    This function registers a new event associated with the current user.
    It requires the user authentication to ensure that the proper user
    context is provided during the creation of the event.

    :param current_user: The authenticated user initiating the event creation.
    :type current_user: Any
    :return: None
    """
    db = Session()
    bl = EventBL(db)

    try:
        contract_id = click.prompt("ID du contrat signé", type=int)
        start_str = click.prompt("Date de début (AAAA-MM-JJ HH:MM)")
        end_str = click.prompt("Date de fin (AAAA-MM-JJ HH:MM)")
        location = click.prompt("Lieu")
        attendees = click.prompt("Nombre de participants", type=int)
        note = click.prompt("Note (optionnel)", default="", show_default=False)

        start_date = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
        end_date = datetime.strptime(end_str, "%Y-%m-%d %H:%M")

        data = {
            "contract_id": contract_id,
            "start_date": start_date,
            "end_date": end_date,
            "location": location,
            "attendees": attendees,
            "note": note or None,
        }

        event = bl.create_event(data, current_user)
        click.echo(f"Évènement crée (ID #{event.id}) pour le contrat {event.contract_id}")

    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")

@event_cli.command("update")
@click.argument("event_id", type=int)
@with_auth_payload
def update_event(event_id, current_user):
    """
    Update the details of an existing event.

    This function allows an authenticated user to update the information
    of a specific event identified by its event ID. It requires the user
    to be authenticated and pass the event ID as well as the user's
    payload.
    - Management can modify any event.
    - Support can modify event for which they are assigned.

    :param event_id: Unique identifier of the event to be updated.
                    Must be an integer.
    :param current_user: The authenticated user attempting to update
                         the event. This contains the user payload
                         from the authentication mechanism.
    :return: None
    """
    db = Session()
    bl = EventBL(db)

    try:
        event = bl.get_event(event_id)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")
        return

    click.echo(f"Évènement actuel (ID #{event.id}) pour le contrat {event.contract_id}")
    click.echo(f" - Début : {event.start_date.strftime('%Y-%m-%d %H:%M')}")
    click.echo(f" - Fin : {event.end_date.strftime('%Y-%m-%d %H:%M')}")
    click.echo(f" - Lieu : {event.location}")
    click.echo(f" - Nombre de participants : {event.attendees}")
    click.echo(f" - Note : {event.note or 'Aucune'}")
    click.echo(f" - Support assigné : {event.support_id or 'Aucun'}")

    updates = {}

    role = current_user.get("role")
    if role == "support":
        if click.confirm("Modifier la date de début ?", default=False):
            new_start = click.prompt("Nouvelle date de début (AAAA-MM-JJ HH:MM)")
            updates["start_date"] = datetime.strptime(new_start, "%Y-%m-%d %H:%M")

        if click.confirm("Modifier la date de fin ?", default=False):
            new_end = click.prompt("Nouvelle date de fin (AAAA-MM-JJ HH:MM)")
            updates["end_date"] = datetime.strptime(new_end, "%Y-%m-%d %H:%M")

        if click.confirm("Modifier le lieu ?", default=False):
            updates["location"] = click.prompt("Nouveau lieu")

        if click.confirm("Modifier le nombre de participants ?", default=False):
            updates["attendees"] = click.prompt("Nouveau nombre de participants", type=int)

        if click.confirm("Modifier la note ?", default=False):
            updates["note"] = click.prompt("Nouvelle note (optionnel)", default="", show_default=False)

    elif role == "management":
        if click.confirm("Modifier le collaborateur support ?", default=False):
            new_support_id = click.prompt("ID du nouveau support (laisser vide pour désassigner)",
                                      default="", show_default=False, type=int)
            updates["support_id"] = int(new_support_id) if new_support_id else None

    else:
        click.echo("Vous n'avez pas les droits pour modifier cet événement.")
        return

    if not updates:
        click.echo("Aucune modification sélectionnée")
        return

    try:
        updated = bl.update_event(event_id, updates, current_user)
        click.echo(f"Événement mis à jour (ID #{updated.id})")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")

@event_cli.command("nosupport")
@with_auth_payload
def list_events_without_support(current_user):
    """
    List all events that do not have support collaborators assigned to them.

    This function interfaces with the system to retrieve events for the
    current user where no support is associated or available. It requires
    an authenticated payload to operate and filters events accordingly.

    :param current_user: The currently authenticated user interacting
        with the system.
    :return: A list of events without support associated for the given user.
    """
    db = Session()
    bl = EventBL(db)

    try:
        events = bl.list_events_without_support(current_user)
        if not events:
            click.echo("Tous les événements ont un support assigné.")
            return

        click.echo("Événements sans support :")
        for e in events:
            click.echo(f" - ID #{e.id} | Début : {e.start_date.strftime('%Y-%m-%d %H:%M')} "
                       f"| {e.end_date.strftime('%Y-%m-%d %H:%M')} | Lieu : {e.location}")

    except PermissionError as pe:
        click.echo(f"Accès refusé : {pe}")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")

@event_cli.command("myevents")
@with_auth_payload
def list_my_events(current_user):
    """
    Lists all events associated with the current user.

    This function retrieves and displays events that are associated with the
    user passed as an argument. The retrieved events are limited to those
    that the current user has access or ownership of, ensuring only
    personalized and relevant entries are displayed.

    :param current_user: The current user whose events are being listed.
    :type current_user: Any
    :return: Events associated with the current user.
    :rtype: list
    """
    db = Session()
    bl = EventBL(db)

    try:
        events = bl.list_events_for_current_support(current_user)
        if not events:
            click.echo("Aucun événement ne vous est assigné.")
            return

        click.echo("Vos événements à venir :")
        for e in events:
            click.echo(f" - ID #{e.id} | Début : {e.start_date.strftime('%Y-%m-%d %H:%M')} "
                       f"| Fin : {e.end_date.strftime('%Y-%m-%d %H:%M')} | Lieu : {e.location}")

    except PermissionError as pe:
        click.echo(f"Accès refusé : {pe}")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")

@event_cli.command("list")
@with_auth_payload
def list_all_events(current_user):
    """
    Lists all events available to the current user. This function retrieves and
    displays a list of events that the authenticated user has access to.

    :param current_user: The currently authenticated user requesting the list of
                         events.
    :type current_user: User
    :return: A list of events accessible to the authenticated user.
    :rtype: list
    """
    db = Session()
    bl = EventBL(db)

    try:
        events = bl.list_all_events()
        if not events:
            click.echo("Aucun événement enregistré.")
            return

        click.echo("Tous les événements :")
        for e in events:
            label_support = f"Support : {e.support_id}" if e.support_id else "Aucun support"
            click.echo(
                f" - ID #{e.id} | {e.start_date.strftime('%Y-%m-%d %H:%M')} → {e.end_date.strftime('%Y-%m-%d %H:%M')}"
                f" | Lieu : {e.location} | Participants : {e.attendees} | {label_support}"
            )

    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur : {e}")

