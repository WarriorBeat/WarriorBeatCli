"""
    utils.py
    Utilities for WarriorBeatCLI

"""
from click import secho, style
import re


class ServiceLog:
    """Logging for Services"""

    def __init__(self, service_name, base_color, **kwargs):
        self.is_root = kwargs.get('root', False)
        self.parent_name = style(
            f"[WBCLI] \u276f", fg='bright_blue', bold=True)
        self.base_color = base_color
        self.service_name = style(
            f"[{service_name}] \u276f", fg=self.base_color)
        self.info_color = kwargs.get('info_color', 'white')
        self.special_color = kwargs.get('special_color', 'yellow')

    def parse_msg(self, msg):
        msg_special = re.findall(r'\$\[(.*?)\]', msg)
        for w in msg_special:
            msg = msg.replace(f"$[{w}]", style(
                w, fg=self.special_color, bold=True))
        return msg

    def echo(self, msg, **kwargs):
        color = kwargs.pop('color', self.base_color)
        title = f"{self.parent_name} {self.service_name if not self.is_root else ''}"
        message = self.parse_msg(msg)
        secho(
            f"{title} ", nl=False, fg=color)
        secho(message, **kwargs)

    def info(self, msg, **kwargs):
        return self.echo(msg, fg=self.info_color, **kwargs)

    def error(self, msg, **kwargs):
        return self.echo(msg, color='red', **kwargs)
