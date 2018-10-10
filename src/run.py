"""
    run.py
    Command Line Interface for WarriorBeat

"""

import os

import click

from services import Service
from utils import ServiceLog

s = ServiceLog('WBCLI', 'bright_blue', root=True)


@click.group()
def cli():
    """
    Simple Command line tool for managing WarriorBeat Services
    """


@cli.command()
@click.argument('profile')
def setaws(profile):
    """Set AWS Profile to Use"""
    os.environ['AWS_PROFILE'] = profile
    click.secho('AWS Profile Set to: ', fg='green', nl=False)
    click.secho(f'{profile}', fg='cyan', bold=True)


@cli.group()
def api():
    """
    WarriorBeatApi Management
    """
    click.echo()


@api.command()
@click.argument('service', default='all', type=click.Choice([*Service.SERVICE_LIST, 'all']))
def start(service):
    """
    Starts the various services used during API development
    """
    if service == 'all':
        s.info(
            f"Starting all services: $[{', '.join(map(str, [s for s in Service.SERVICE_LIST]))}]\n")
        return [Service(s).start() for s in Service.SERVICE_LIST if s != 'api']
    service = Service(service)
    s.info(f"Starting $[{service.name}]\n")
    service.start()


@api.command()
@click.argument('service', default='all', type=click.Choice(['all', 's3', 'db', 'api']))
def stop(service):
    """Stops any running service"""
    if service == 'all':
        s.info(
            f"Stopping all services: $[{', '.join(map(str, [s for s in Service.SERVICE_LIST]))}]\n")
        return [Service(s).stop() for s in Service.SERVICE_LIST if s != 'api']
    service = Service(service)
    s.info(f"Stopping $[{service.name}]\n")
    service.stop()


@api.command()
@click.argument('service', default='all', type=click.Choice(['all', 's3', 'db', 'api']))
def restart(service):
    """Restarts the given service"""
    if service == 'all':
        return [Service(s).restart() for s in Service.SERVICE_LIST if s != 'api']
    service = Service(service)
    s.info(f"Restarting $[{service.name}]")
    service.restart()
