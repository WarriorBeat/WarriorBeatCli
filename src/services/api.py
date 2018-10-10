"""
    services/api.py
    Deals with managing the Flask Api Server
"""

from .service import GenericService

API = {
    'api': {
        'name': 'warriorbeat'
    }
}


class APIService(GenericService):
    """API Type Services"""
    SERVICES = API

    def start(self):
        print('I am starting something from API')
