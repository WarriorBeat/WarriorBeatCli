"""
    services/docker.py
    Manages Docker Containers used by WarriorBeat
"""


import docker

from utils import ServiceLog

from .service import GenericService

DOCKER = {
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


class DockerService(GenericService):
    """Management for docker related services"""
    SERVICES = DOCKER

    def __init__(self, id, debug=False, live=False):
        self.id = id
        self.live = live
        self.log = ServiceLog('Docker', 'cyan')
        self.client = self._get_client()
        self.data = self.SERVICES[self.id]
        self.name = self.data['name']
        self.container = self._get_container()

    def _get_client(self):
        """creates a docker client"""
        client = docker.from_env()
        try:
            client.ping()
            return client
        except Exception as e:
            self.log.clear()
            self.log.exception(e)
            return self.log.error('The Docker Service is not Running.')

    def _get_container(self):
        """retrieve a docker container"""
        client = self.client.containers
        try:
            container = client.get(self.name)
            return container
        except:
            return None

    def _create(self):
        """creates container"""
        client = self.client.containers
        self.log.info(f"Container $[{self.name}] not found. Creating now...")
        container = client.create(**self.data, detach=True)
        return container

    def _is_running(self, container=None):
        """checks if a container is running"""
        container = container or self.container
        try:
            return True if container.status == 'running' else False
        except AttributeError:
            return False

    def start(self):
        """starts container"""
        if self.live:
            return self.log.warn(f"{self.name} cannot run in live mode.\n")
        if self.container:
            self.log.info(
                f"Found container $[{self.name}] $[({self.container.short_id})]")
        else:
            self.container = self._create()
        container_id = f"$[{self.name}] $[({self.container.short_id})]"
        if self._is_running():
            return self.log.warn(f"{container_id} is already $w[running!]\n")
        self.log.info(
            f"Starting {container_id} on ports $w[{self.data['ports']}]")
        self.container.start()
        self.log.info(f"{container_id} is $w[live!]\n")

    def stop(self):
        """stops container"""
        _is_not_running = f"$[{self.name}] is not running!"
        _container_id = f"$[{self.name}] $[({self.container.short_id})]"
        if not self.container:
            return self.log.error(_is_not_running)
        if not self._is_running():
            return self.log.error(_is_not_running)
        self.log.info(f'Found container {_container_id}, stopping...')
        self.container.stop()
        self.log.info(f"{_container_id} has been stopped!\n")

    def restart(self):
        """restarts container"""
        _container_id = f"$[{self.name}] $[({self.container.short_id})]"
        if not self._is_running():
            return self.log.error(f"{_container_id} is not running!")
        self.log.info(f"{_container_id} is restarting...")
        self.container.restart()
        self.log.info(f"{_container_id} is $w[live!]\n")

    def status(self):
        status = [self.name]
        status.append(True if self._is_running() is not False else False)
        return status
