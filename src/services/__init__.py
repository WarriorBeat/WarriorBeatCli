"""
    services/__init__.py
    Entry point for services. Contains Service Factory
"""

from .docker import DockerService
from .api import APIService


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


Service = ServiceManager
