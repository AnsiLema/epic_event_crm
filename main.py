import click
from monitoring.sentry_logging import init_sentry
from cli.auth_commands import auth_cli
from cli.collaborator_commands import collaborator_cli
from cli.contract_commands import contract_cli
from cli.client_commands import client_cli
from cli.init_command import init_cli
from cli.event_commands import event_cli


init_sentry()


@click.group()
def cli():
    """
    CLI for Epic Events CRM
    """
    pass


cli.add_command(init_cli)
cli.add_command(auth_cli)
cli.add_command(collaborator_cli)
cli.add_command(client_cli)
cli.add_command(contract_cli)
cli.add_command(event_cli)


if __name__ == "__main__":
    cli()
