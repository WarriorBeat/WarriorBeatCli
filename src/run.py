"""
    run.py
    Command Line Interface for WarriorBeat

"""

import click
import os
import time
from tqdm import tqdm
from services import docker
from utils import ServiceLog
from tabulate import tabulate

s = ServiceLog('WBCLI', 'bright_blue', root=True)


@click.group()
def cli():
    """
    Simple Command line tool for managing WarriorBeat Services
    """
    pass


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
    pass


SERVICES = ['all', 's3', 'db', 'api']


@api.command()
@click.argument('service', default='all', type=click.Choice(SERVICES))
def start(service):
    """
    Starts the various services used during API development
    """
    dock_services = ['db', 's3']
    if service is 'all':
        s.info(
            f"Starting: $[{', '.join(map(str, [s for s in SERVICES if s != 'all']))}]")
        return [docker.start(con) for con in dock_services]
    s.info(f"Starting $[{service}]")
    if service in ['db', 's3']:
        docker.start(service)


@api.command()
@click.argument('service', default='all', type=click.Choice(['all', 's3', 'db', 'api']))
def stop(service):
    """Stops any running service"""
    dock_services = ['db', 's3']
    if service is 'all':
        s.info(
            f"Stopping: $[{', '.join(map(str, [s for s in SERVICES if s != 'all']))}]")
        return [docker.stop(con) for con in dock_services]
    s.info(f"Stopping $[{service}]")
    if service in ['db', 's3']:
        docker.stop(service)


@api.command()
def status():
    """get status of running services"""
    status = [['Service', 'Is Running']]
    dock_stat = docker.status()
    status.extend(dock_stat)
    # click.echo(status)
    click.echo(tabulate(status, headers="firstrow",
                        tablefmt='fancy_grid', stralign="center"))
