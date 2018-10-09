"""
    services/docker.py
    management for docker related services

"""

import click
import docker

from utils import ServiceLog


DOCKER_CONTAINERS = {
    'db': {
        'image': 'amazon/dynamodb-local',
        'ports': {8000: 8000},
        'name': 'localdynamo'
    },
    's3': {
        'image': 'scality/s3server:mem-latest',
        'ports': {9000: 8000},
        'name': 's3server'
    },
}

s = ServiceLog('Docker', 'cyan')


def get_client():
    """get a docker client"""
    dock_client = docker.from_env()
    try:
        dock_client.ping()
        return dock_client
    except Exception as e:
        click.clear()
        click.secho(e.__str__(), fg='bright_red')
        click.secho('The Docker Service is not Running',
                    fg='red', underline=True)


def start(container):
    """starts a docker container"""
    client = get_client().containers
    cont = DOCKER_CONTAINERS[container]
    try:
        container = client.get(cont['name'])
        if container.status == 'running':
            return s.info(f"Container $[{cont['name']}] is already running!")
        s.info(
            f"Found $[{cont['name']}] $[({container.short_id})] container, running now.")
        container.start()
    except:
        s.info(f"Container $[{cont['name']}] not found. Creating now...")
        cont = client.run(
            cont['image'], ports=cont['ports'], name=cont['name'], detach=True)
        s.info(f"$[{cont.name}] $[{cont.short_id}] created, running now.")


def stop(container):
    """stops a container"""
    client = get_client().containers
    cont = DOCKER_CONTAINERS[container]
    try:
        container = client.get(cont['name'])
        if container.status == 'exited':
            return s.info(f"Container $[{cont['name']}] already stopped!")
        container.stop()
        s.info(f"Stopped $[{cont['name']}] container.")
    except docker.errors.NotFound:
        s.error(f"Container $[{cont['name']}] does not exist!")
    except docker.errors.APIError as e:
        s.error(f"Failed to stop $[{cont['name']}] container!")
        s.error(str(e))


def status():
    """docker status"""
    client = get_client().containers
    status = []
    for c in DOCKER_CONTAINERS.values():
        c_stat = []
        c_stat.append(c['name'])
        try:
            cont = client.get(c['name'])
            is_running = click.style(
                '\u2714', fg='green') if cont.status == 'running' else click.style('\u2716', fg='red')
        except:
            cont = c
            is_running = False
        c_stat.append(is_running)
        status.append(c_stat)
    return status
