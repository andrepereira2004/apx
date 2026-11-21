"""Recognize a trusted fresh portable installation without pilot identities."""
import json
from pathlib import Path
import stat


def installed(path=Path('/var/lib/apx/portable-graphical-install.json')):
    if not path.exists():
        return False
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_gid or info.st_mode & 0o022 or info.st_size > 262144:
        raise ValueError('Untrusted portable installation record')
    value = json.loads(path.read_text())
    return value.get('schema') == 1 and value.get('profile') == 'portable-graphical-v1'


def stop_hub_command():
    if installed():
        return ['/usr/bin/systemctl', 'stop', 'apx-portable-graphical.service']
    return ['/var/lib/apx/official-hub-v1/apx-official-hub-graphical-v1.py', '--recover']
