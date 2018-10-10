"""
    services.py
    Classes for the various services used by WarriorBeat
"""

import docker

from utils import ServiceLog


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

API = {
    'api': {
        'name': 'warriorbeat'
    }
}


class GenericService():
    """Generic Service Base Class"""
    SERVICES = None

    def __init__(self, id):
        self.id = id

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def restart(self):
        raise NotImplementedError()

    @classmethod
    def supports(cls, id):
        return True if id in cls.SERVICES else False


class DockerService(GenericService):
    """Management for docker related services"""
    SERVICES = DOCKER

    def __init__(self, id):
        self.id = id
        self.log = ServiceLog('Docker', 'cyan')
        self.client = self._get_client()
        self.data = self.SERVICES[self.id]
        self.name = self.data['name']
        self.container = self._get_container()

    def _get_client(self):
        """get a docker client"""
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
        client = self.client.containers
        self.log.info(f"Container $[{self.name}] not found. Creating now...")
        container = client.create(**self.data, detach=True)
        return container

    def _is_running(self, container=None):
        """checks if a container is running"""
        container = container or self.container
        return True if container.status == 'running' else False

    def start(self):
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
        _container_id = f"$[{self.name}] $[({self.container.short_id})]"
        if not self._is_running():
            return self.log.error(f"{_container_id} is not running!")
        self.log.info(f"{_container_id} is restarting...")
        self.container.restart()
        self.log.info(f"{_container_id} is $w[live!]\n")


class APIService(GenericService):
    """API Type Services"""
    SERVICES = API

    def start(self):
        print('I am starting something from API')


class ServiceManager:
    """Factory for Services"""
    PROVIDERS = [DockerService, APIService]
    SERVICE_LIST = [
        serv for prov in PROVIDERS for serv in list(prov.SERVICES.keys())]

    def __init__(self, id, *args, **kwargs):
        self.id = id
        self.service = self.get_service(*args, **kwargs)
        self.name = self.service.name

    def get_service(self, *args, **kwargs):
        for provider in self.PROVIDERS:
            if provider.supports(self.id):
                return provider(self.id, *args, **kwargs)
        assert hasattr(
            self, 'service') == True, f"{self.id} is not a valid service!"

    def start(self):
        self.service.start()

    def stop(self):
        self.service.stop()

    def restart(self):
        self.service.restart()
