"""
    utils.py
    Utilities for WarriorBeatCLI

"""
import configparser
import re
from pathlib import Path

from click import clear, confirm, prompt, secho, style


class ServiceLog:
    """Logging for Services"""

    def __init__(self, service_name, base_color, **kwargs):
        self.is_root = kwargs.get('root', False)
        self.parent_name = style(
            f"[WBCLI] \u276f", fg='bright_blue', bold=True)
        self.base_color = base_color
        self.service_name = service_name
        self.info_color = kwargs.get('info_color', 'white')
        self.accent_color = kwargs.get('accent_color', 'yellow')
        self.warn_color = kwargs.get('warn_color', 'green')
        self.config_path = Path.home() / '.wbcli'

    def parse_msg(self, msg, accent_color=None):
        msg_special = re.findall(r'\$(.*?)\[(.*?)\]', msg)
        color = accent_color or self.accent_color
        for w in msg_special:
            if w[0] == 'w':
                color = self.warn_color
            msg = msg.replace(f"${w[0]}[{w[1]}]", style(
                w[1], fg=color))
        return msg

    def get_service(self, **kwargs):
        color = kwargs.pop('fg', self.base_color)
        title = style(
            f"[{self.service_name}] \u276f", fg=color, **kwargs)
        return title

    def echo(self, msg, **kwargs):
        title_color = kwargs.pop('title_color', self.base_color)
        title_bold = kwargs.pop('title_bold', False)
        accent_color = kwargs.pop('accent', self.accent_color)
        service_title = self.get_service(fg=title_color, bold=title_bold)
        title = f"{self.parent_name} {service_title if not self.is_root else ''}"
        message = self.parse_msg(msg, accent_color)
        secho(
            f"{title} ", nl=False)
        secho(message, **kwargs)

    def info(self, msg, **kwargs):
        return self.echo(msg, **kwargs)

    def error(self, msg, **kwargs):
        return self.echo(msg, title_color='red', title_bold=True, fg='red', underline=True, accent='red', **kwargs)

    def warn(self, msg, **kwargs):
        return self.echo(msg, title_color='red', title_bold=True)

    def exception(self, error, **kwargs):
        return self.echo(str(error), title_color='red', title_bold=True, **kwargs)

    def prompt(self, msg, **kwargs):
        new_line = kwargs.pop('nl', False)
        nl_default = kwargs.get('default', None)
        msg = self.parse_msg(msg)
        msg = msg + \
            style(f"\n Press Enter to Use: [{nl_default}]", dim=True) if nl_default and len(
                nl_default) > 0 else msg
        title = self.get_service()
        suffix = style('\u27a4 ', fg=self.accent_color)
        secho(f"{self.parent_name} {title} ", nl=False)
        return prompt(msg + '\n' if new_line else msg,
                      prompt_suffix=suffix, **kwargs)

    def confirm(self, msg, **kwargs):
        msg = self.parse_msg(msg)
        title = self.get_service()
        suffix = style('\u27a4 ', fg=self.accent_color)
        secho(f"{self.parent_name} {title} ", nl=False)
        return confirm(msg, show_default="[y/N] ", prompt_suffix=suffix, **kwargs)

    def save(self, section, key, value):
        if not self.config_path.exists():
            self.config_path.mkdir(parents=True, exist_ok=True)
        config_file = self.config_path / 'config.ini'
        config = configparser.ConfigParser()
        if config_file.exists():
            config.read(config_file)
        try:
            config.set(section, key, value)
        except configparser.NoSectionError:
            config.add_section(section)
            config.set(section, key, value)
        with config_file.open(mode='w') as cfile:
            config.write(cfile)

    def retrieve(self, section, key):
        config_file = self.config_path / 'config.ini'
        config = configparser.ConfigParser()
        try:
            config.read(config_file)
            return config.get(section, key)
        except Exception:
            return None

    def diff_print(self, diff):
        for line in iter(diff, b''):
            line = line.decode('utf-8').rstrip()
            if line.startswith('+++'):
                yield secho(line, fg='bright_blue', nl=False)
            elif line.startswith('---'):
                yield secho(f"\n{line}", fg='blue', nl=False, dim=True)
            elif line.startswith('-'):
                yield secho(line, fg='bright_red', nl=False)
            elif line.startswith('+'):
                yield secho(line, fg='green', nl=False)
            elif line.startswith('@'):
                yield secho(line, fg='bright_yellow', nl=False)
            else:
                yield line

    def clear(self):
        """Clears terminal screen"""
        return clear()
