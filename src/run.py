"""
    run.py
    Command Line Interface for WarriorBeat

"""

import os

import click

from services import Service
from utils import ServiceLog
from tabulate import tabulate
from art import text2art

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


@cli.command()
def status():
    '''
    View active services
    '''
    s.clear()
    title = text2art('WB CLI', font='swampland')
    run = click.style('\u2714', fg='green')
    stop = click.style('\u2718', fg='red')
    _status = [Service(s).status() for s in Service.SERVICE_LIST]
    status = [list(run if r == True else stop if r == False else r for r in st)
              for st in _status]
    click.secho(title, fg='bright_cyan')
    click.echo(tabulate(status, headers=[
               'Service', 'Running'], tablefmt="fancy_grid", stralign="center"))


@cli.group()
def api():
    """
    WarriorBeatApi Management
    """
    click.echo()


@api.command()
@click.option('--debug/-d', help='Display Flask Debug Output', is_flag=True)
@click.option('--live', help='Connect to AWS Server', is_flag=True)
@click.argument('service', default='all', type=click.Choice([*Service.SERVICE_LIST, 'all']))
def start(service, debug, live):
    """
    Starts the various services used during API development
    """
    if service == 'all':
        s.info(
            f"Starting all services: $[{', '.join(map(str, [s for s in Service.SERVICE_LIST]))}]\n")
        return [Service(s, debug=debug, live=live).start() for s in Service.SERVICE_LIST]
    service = Service(service, debug=debug, live=live)
    s.info(f"Starting $[{service.name}]\n")
    service.start()


@api.command()
@click.argument('service', default='all', type=click.Choice(['all', 's3', 'db', 'api']))
def stop(service):
    """Stops any running service"""
    if service == 'all':
        s.info(
            f"Stopping all services: $[{', '.join(map(str, [s for s in Service.SERVICE_LIST]))}]\n")
        return [Service(s).stop() for s in Service.SERVICE_LIST]
    service = Service(service)
    s.info(f"Stopping $[{service.name}]\n")
    service.stop()


@api.command()
@click.argument('service', default='all', type=click.Choice(['all', 's3', 'db', 'api']))
def restart(service):
    """Restarts the given service"""
    if service == 'all':
        return [Service(s).restart() for s in Service.SERVICE_LIST]
    service = Service(service)
    s.info(f"Restarting $[{service.name}]")
    service.restart()


@cli.group()
def app():
    '''
    WarriorBeatApp Management
    '''
    click.echo()


# @app.command()
# def start():
#     pass
