"""
    services/api.py
    Deals with managing the Flask Api Server
"""

import os
import subprocess as subp
import threading
from pathlib import Path
from time import sleep

import boto3
import click
import psutil
import requests
import yaml
from botocore.exceptions import ClientError
from git import Repo

from utils import ServiceLog, ch_dir

from . import resource as res
from . import scrape
from .service import GenericService

FLASK = {
    'api': {
        'name': 'WarriorBeatApi',
        'origin_url': 'github.com/WarriorBeat/WarriorBeatApi',
        'port': '5000',
        'env': {'FLASK_APP': 'warriorbeat', 'FLASK_ENV': 'development', 'FLASK_TESTING': 'True', 'AWS_DEV': 'True'},
        'args': "pipenv run flask run",
    }
}


class APIService(GenericService):
    """API Type Services"""
    SERVICES = FLASK

    def __init__(self, id, **kwargs):
        self.id = id
        self.log = ServiceLog('API', 'bright_magenta')
        self.data = FLASK[self.id]
        self.name = self.data['name']
        self.path = None
        self.debug = kwargs.get("debug", False)
        self.live = kwargs.get("live", False)
        self.is_test = kwargs.get("test", False)
        self.upload_sample = kwargs.get("sample_data", False)
        self.upload_scrape = kwargs.get("scrape_data", False)
        self.ngrok = kwargs.get("ngrok", False)

    def _validate_path(self, path):
        try:
            repo = Repo(path)
            full_url = repo.remotes.origin.url
            url = full_url.split('://')[1]
            assert url == self.data['origin_url'] or url == self.data['origin_url'] + '.git'
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
                    f'Found path in config ({"..." + str(path)[-15:]})')
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

    def _is_running(self, conf_id='PID'):
        """checks if api is running"""
        try:
            last_pid = int(self.log.retrieve('API', conf_id))
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
        outp = None
        if self.debug:
            outp = threading.Thread(
                target=self._output_flask, args=(flask_proc, ))
        self.log.info(f"API started on port $[{self.data['port']}]")
        self.log.save('API', 'PID', str(flask_proc.pid))
        if not self.is_test and not self.live:
            try:
                self.setup_resources()
            except ClientError:
                self.log.warn("Resources already exist!")
            if self.upload_sample:
                self.log.info("Uploading sample data...")
                res.upload_sample_data(self.log)
            if self.upload_scrape:
                self.log.info("Scraping and Uploading data...")
                scrape.upload_scraped_data(self.log)
        self.log.info(f'$[{self.name}] is $w[live!]\n')
        # Handle Ngrok
        if self.ngrok:
            self.create_ngrok()
        if outp is not None:
            outp.start()
        return flask_proc

    def setup_resources(self):
        """creates database tables and buckets"""
        self.log.info("Creating resources...")
        dbclient = boto3.resource(
            'dynamodb', region_name='localhost', endpoint_url='http://localhost:8000')
        s3client = boto3.client('s3', region_name='localhost',
                                endpoint_url='http://localhost:9000',
                                aws_access_key_id='accessKey1', aws_secret_access_key='verySecretKey1')
        s3resource = boto3.resource(
            's3', region_name='localhost', endpoint_url='http://localhost:9000', aws_access_key_id='accessKey1', aws_secret_access_key='verySecretKey1')
        self.resources = {}
        self.resources['tables'] = [res.create_table(
            dbclient, res.TABLES[t], self.log) for t in res.TABLES]
        self.resources['buckets'] = [res.create_bucket(
            s3client, s3resource, res.BUCKETS[b], self.log) for b in res.BUCKETS]
        return self.resources

    def get_ngrok_config(self):
        """retrieves/creates ngrok config"""
        self.log.info("Fetching $[ngrok] config...")
        saved_config = self.log.retrieve("API", "NGROK_CONFIG")
        if saved_config:
            return saved_config
        self.log.info("Config not found, creating one now...")
        auth = self.log.prompt("What is your ngrok auth code? ",
                               show_default=False, nl=True)
        config = {
            'authtoken': auth,
            'tunnels': {
                'api': {
                    'addr': self.data['port'],
                    'proto': 'http'
                }
            }
        }
        config_file = Path(self.log.config_path / 'ngrok.yml')
        with config_file.open('w') as conf:
            yaml.dump(config, conf, default_flow_style=False)
        config_file = str(config_file.resolve())
        self.log.save("API", "NGROK_CONFIG", config_file)
        self.log.info(
            f'Config saved to => ({"..." + str(config_file)[-15:]})')
        return config_file

    def retrieve_ngrok_tunnel(self):
        """retrieves public ngrok tunnel url"""
        tunnel_endpoint = "http://localhost:4040/api/tunnels"
        retr = requests.get(tunnel_endpoint).json()
        tunnel = retr['tunnels'][0]['public_url']
        return tunnel

    def create_ngrok(self):
        """creates ngrok tunnel for api"""
        if self._is_running(conf_id="NGROK_PID"):
            tunnel = self.retrieve_ngrok_tunnel()
            return self.log.info(f"$[ngrok] tunnel already running at \u279C $w[{tunnel}]")
        config = self.get_ngrok_config()
        self.log.info("Config loaded...")
        self.log.info(
            f"Starting $[ngrok] tunnel on port $w[{self.data['port']}]")
        ngrok_proc = psutil.Popen(f"ngrok start -config {config} api", stdout=subp.DEVNULL,
                                  stderr=subp.STDOUT, shell=True)
        self.log.save('API', 'NGROK_PID', str(ngrok_proc.pid))
        sleep(5)  # lazily giving ngrok time to start
        tunnel = self.retrieve_ngrok_tunnel()
        self.log.info(f'$[ngrok] tunnel launched at \u279C $w[{tunnel}]')

    def kill_ngrok(self):
        """kills ngrok process if running"""
        pid = self._is_running(conf_id="NGROK_PID")
        if pid:
            self.log.info("Terminating ngrok tunnel...")
            ngrok_proc = psutil.Process(pid)
            ngrok_proc.terminate()
            self.log.save("API", "NGROK_PID", "")
            return self.log.info(f"$[ngrok] tunnel has been stopped!")
        return False

    def stop(self):
        """stops api service"""
        pid = self._is_running()
        if not pid:
            return self.log.error(f"{self.name} is not running!")
        self.kill_ngrok()
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
