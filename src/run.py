"""
    run.py
    Command Line Interface for WarriorBeat
    
    Rapidly put together with the sole purpose of working
    for WarriorBeat purposes. Not the most clean program out there...
"""

import os
import subprocess as subp
import time

import click
from art import text2art
from tabulate import tabulate

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


@cli.command()
@click.option('--in-place', help='Make the changes', is_flag=True)
@click.argument('path', type=click.Path(exists=True, resolve_path=True), default='.')
def clean(path, in_place):
    '''
    Recursively clean project with autoflake, autopep8, and isort.
    Requires autoflake, autopep8, and isort.
    Default: Current Directory
    '''
    s.info("Running autoflake...")
    flake_args = ['autoflake', '--remove-all-unused-imports', '-r', path]
    if in_place:
        del flake_args[3]
        flake_args.extend(['--in-place', path])
    flake_proc = subp.Popen(flake_args, stdout=subp.PIPE)
    for l in s.diff_print(flake_proc.stdout.readline):
        click.echo(l)
    s.info('Autoflake complete')
    s.info('Starting autopep8...')
    time.sleep(3)
    pep_args = ['autopep8', '-rd', path]
    if in_place:
        pep_args[1] = '-ri'
    pep_proc = subp.Popen(pep_args)
    s.info('Autopep8 complete')
    s.info('Starting isort...')
    time.sleep(3)
    sort_args = ['isort', '-rc', '--diff', '--check-only', path]
    if in_place:
        del sort_args[2]
        del sort_args[2]
    sort_proc = subp.Popen(sort_args, stdout=subp.PIPE)
    for l in s.diff_print(sort_proc.stdout.readline):
        click.echo(l)
    s.info('Cleaning Complete')


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
@click.option('--debug', '-d', help='Display Flask Debug Output', is_flag=True)
@click.option('--live', '-l', help='Connect to AWS Server', is_flag=True)
@click.option('--test', '-t',  help='Skips resource creation (for Unit tests)', is_flag=True)
@click.argument('service', default='all', type=click.Choice([*Service.SERVICE_LIST, 'all']))
def start(service, debug, live, test):
    """
    Starts the various services used during API development
    """
    if service == 'all':
        s.info(
            f"Starting all services: $[{', '.join(map(str, [s for s in Service.SERVICE_LIST]))}]\n")
        return [Service(s, debug=debug, live=live, test=test).start() for s in Service.SERVICE_LIST]
    service = Service(service, debug=debug, live=live, test=test)
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
