"""
    services/app.py
    Manages WarriorBeatApp
"""

from .service import GenericService

NODE = {
    'app': {
        'name': 'WarriorBeatApp',
        'origin_url': 'https://github.com/WarriorBeat/WarriorBeatApp.git',
        'flags': [
            ('', 'start'),
            ('-a', 'android'),
            ('-d', 'debug'),
            ('-n', 'node')
        ],
        'args': ['flask', 'run', '-p']
    }
}


class AppService(GenericService):
    """App Type Services"""
    SERVICES = NODE

    def __init__(self, id, flags):
        self.id = id
        self.flags = flags

    def start(self):
        print(self.id, self.flags)
        return True
