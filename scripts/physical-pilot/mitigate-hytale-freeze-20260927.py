#!/usr/bin/env python3
"""Bounded, reversible Hytale graphics-load trial on the physical pilot."""

import json
import os
from pathlib import Path
import shutil
import tempfile


SETTINGS = Path('/var/lib/apx/environments/hytale/home/apx/.var/app/com.hypixel.HytaleLauncher/data/Hytale/UserData/Settings.json')
BACKUP = Path('/var/lib/apx/backups/20260927T-hytale-graphics-load-trial/Settings.json')


def main():
    if os.uname().nodename != 'apx-host':
        raise SystemExit('Unexpected Host')
    if BACKUP.exists():
        raise SystemExit('Backup already exists; refusing repeat edit')
    original = SETTINGS.read_bytes()
    config = json.loads(original)
    rendering = config['RenderingSettings']
    if (config['FpsLimit'], config['UnlimitedFps'], rendering['ViewDistance']) != (240, False, 384):
        raise SystemExit('Unexpected Hytale graphics settings')
    config['FpsLimit'] = 60
    rendering['ViewDistance'] = 128
    edited = json.dumps(config, ensure_ascii=False, indent=2).encode() + b'\n'
    stat = SETTINGS.stat()
    BACKUP.parent.mkdir(parents=True, exist_ok=False)
    shutil.copy2(SETTINGS, BACKUP)
    os.chown(BACKUP, stat.st_uid, stat.st_gid)
    if BACKUP.read_bytes() != original:
        raise SystemExit('Backup verification failed')
    descriptor, temporary = tempfile.mkstemp(prefix='.Settings-', dir=SETTINGS.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(edited)
            stream.flush()
            os.fsync(stream.fileno())
        os.chown(temporary, stat.st_uid, stat.st_gid)
        os.chmod(temporary, stat.st_mode & 0o777)
        os.replace(temporary, SETTINGS)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    if SETTINGS.read_bytes() != edited:
        raise SystemExit('Installed settings verification failed')
    print(f'Installed Hytale trial: FPS 60, view distance 128; backup {BACKUP}')


if __name__ == '__main__':
    main()
