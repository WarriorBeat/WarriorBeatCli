"""
    services/api.py
    Deals with managing the Flask Api Server
"""

import os
import subprocess as subp
import threading
from pathlib import Path

import click
import psutil
from git import Repo

from utils import ServiceLog, ch_dir

from .service import GenericService

FLASK = {
    'api': {
        'name': 'WarriorBeatApi',
        'origin_url': 'https://github.com/WarriorBeat/WarriorBeatApi.git',
        'port': '5000',
        'env': {'FLASK_APP': 'warriorbeat', 'FLASK_ENV': 'development', 'FLASK_TESTING': 'True'},
        'args': "pipenv run flask run"
    }
}


class APIService(GenericService):
    """API Type Services"""
    SERVICES = FLASK

    def __init__(self, id, debug=False, live=False):
        self.id = id
        self.log = ServiceLog('API', 'bright_magenta')
        self.data = FLASK[self.id]
        self.name = self.data['name']
        self.path = None
        self.debug = debug
        self.live = live

    def _validate_path(self, path):
        try:
            repo = Repo(path)
            url = repo.remotes.origin.url
            assert url == self.data['origin_url']
            return path
        except AssertionError:
            self.log.error(f'{path} is not the WarriorBeatApi Repo')
            raise click.Abort()
        except:
            self.log.error(f'{path} is not a valid git repository.')
            raise click.Abort()

    def _get_path(self):
        env = os.environ.get('API_DIR', None)
        if env is None:
            path_config = self.log.retrieve('PATH', 'API_DIR')
            if path_config is not None:
                path = Path(path_config)
                self.log.info(
                    f'Found path in config ({"..." + str(path)[-25:]})')
                return path
            path = self.log.prompt('Where is your WarriorBeatApi located? ',
                                   default=env, show_default=False, nl=True, type=click.Path(resolve_path=True))
        path = self._validate_path(path)
        if path:
            path = Path(path)
            os.environ['API_DIR'] = str(path.resolve())
            if str(path) != env:
                do_save = self.log.confirm('Do you want to save this path?')
                if do_save:
                    self.log.save('PATH', 'API_DIR', str(path.resolve()))
                    self.data['env']['API_DIR'] = str(path.resolve())
        return path

    def _is_running(self):
        """checks if api is running"""
        try:
            last_pid = int(self.log.retrieve('API', 'PID'))
            return last_pid if psutil.pid_exists(last_pid) is True else False
        except:
            return False

    def _output_flask(self, proc):
        for l in iter(proc.stdout.readline, b''):
            print(l.decode('utf-8'), end='')

    def start(self):
        """starts wbapi flask service"""
        if self._is_running():
            return self.log.warn(f"$[{self.name}] is already $w[running!]")
        self.path = self._get_path()
        self.log.info('Setting Flask environment variables...')
        for evar in self.data['env']:
            if self.live and evar == 'FLASK_TESTING':
                self.data['env'][evar] = 'False'
            env_val = self.data['env'][evar]
            self.log.info(
                f"$[{evar}] \u279C $w[{'...' + env_val[20:] if len(env_val) > 20 else env_val}]")
        args = self.data['args']
        args = args + f" -p {self.data['port']}"
        out = subp.DEVNULL
        if self.debug:
            out = subp.PIPE
        try:
            with ch_dir(self.path):
                flask_proc = psutil.Popen(args, stdout=out, stderr=subp.STDOUT, cwd=str(
                    self.path), shell=True, env=dict(os.environ, **self.data['env']))
        except FileNotFoundError:
            return self.log.error(f"This service requires the $[Flask] python microframework.")
        if self.debug:
            outp = threading.Thread(
                target=self._output_flask, args=(flask_proc, ))
            outp.start()
        self.log.info(f"API started on port $[{self.data['port']}]")
        self.log.save('API', 'PID', str(flask_proc.pid))
        return self.log.info(f'$[{self.name}] is $w[live!]')

    def stop(self):
        """stops api service"""
        pid = self._is_running()
        if not pid:
            return self.log.error(f"{self.name} is not running!")
        self.log.info("Terminating flask process...")
        flask_proc = psutil.Process(pid)
        flask_proc.terminate()
        self.log.save('API', 'PID', '')
        return self.log.info(f'$[{self.name}] has been stopped!')

    def restart(self):
        """restarts api service"""
        self.log.info(f"$[{self.name}] is restarting...")
        self.stop()
        self.start()

    def status(self):
        status = [self.name]
        status.append(True if self._is_running() is not False else False)
        return status
