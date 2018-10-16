"""
    services.py
    Classes for the various services used by WarriorBeat
"""


class GenericService():
    """Generic Service Base Class"""
    SERVICES = None

    def __init__(self, id, debug=False):
        self.id = id
        self.debug = debug

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def restart(self):
        raise NotImplementedError()

    def status(self):
        raise NotImplementedError()

    @classmethod
    def supports(cls, id):
        return True if id in cls.SERVICES else False
