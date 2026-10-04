#!/usr/bin/env python3
"""Deploy the Rofi action symbols and terminal removal choice to pilot workloads."""

import argparse
import ast
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

REPO = Path(__file__).resolve().parents[2]
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
BASE = Path('/var/lib/apx/environments')
RUNTIME = Path('/usr/lib/apx/apx-lab-runtime.py')
NAMES = ('faculdade', 'hytale', 'minecraft', 'steam')
ASSETS = {
    'local/bin/apx-window-apps-v1': (
        '098a370c3cadfb7fedc04e674a94c438fb71b1a2a0bced6a707f0e489e4694c6',
        '6c37a57be3fade4f4ff7fa187d61d2fc40223c23af25ab7505eea95be056e7a9'),
    'local/bin/apx-application-remove-v1': (
        '5bfe0f4f3b106e4f4aee9dfa096a9fedb218637f805a52f19e5cf249f728fc13',
        '6ac8c31d23239a4e07aba8a04e8ff85ae4c5c90b3a56e7a684cd23ee0d5a77bf'),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def regular(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f'unsafe or missing file: {path}')
    return path.read_bytes()


def runtime_with_pins(data):
    text = data.decode()
    start = text.index('ENVIRONMENT_SHELL_ASSETS = ')
    end = text.index('\n}', start) + 2
    mapping = ast.literal_eval(text[start:end].split(' = ', 1)[1])
    for rel, (before, after) in ASSETS.items():
        if mapping.get(rel) != before:
            raise RuntimeError(f'installed runtime pin differs: {rel}')
        mapping[rel] = after
    replacement = 'ENVIRONMENT_SHELL_ASSETS = ' + json.dumps(mapping, indent=4, sort_keys=True)
    return (text[:start] + replacement + text[end:]).encode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    identity = (Path('/etc/hostname').read_text().strip(),
                Path('/sys/class/dmi/id/product_name').read_text().strip(),
                Path('/sys/class/dmi/id/board_name').read_text().strip())
    if identity != ('apx-host', '82JU', 'LNVNB161216'):
        raise RuntimeError('physical pilot identity differs')
    if 'profile=apx-physical-headless-pilot-v1' not in Path('/etc/apx-physical-pilot').read_text().splitlines():
        raise RuntimeError('physical pilot marker differs')
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if Path('/run/apx/system-power-v1.reserved').exists():
            raise RuntimeError('system power transition reserved')
        for name in NAMES:
            registration = json.loads(regular(BASE / name / 'registration.json'))
            if (registration.get('name'), registration.get('role'), registration.get('state')) != (
                    name, 'graphical-base', 'stopped'):
                raise RuntimeError(f'Environment state differs: {name}')
        changes = []
        for rel, (before, after) in ASSETS.items():
            source = regular(REPO / 'config/environment-shell-v1' / rel)
            if digest(source) != after:
                raise RuntimeError(f'source digest differs: {rel}')
            targets = [SEED / rel] + [BASE / name / 'home/apx/.local/bin' / Path(rel).name
                                      for name in NAMES]
            for target in targets:
                if digest(regular(target)) != before:
                    raise RuntimeError(f'installed baseline differs: {target}')
                changes.append((target, source))
        runtime_before = regular(RUNTIME)
        changes.append((RUNTIME, runtime_with_pins(runtime_before)))
        for target, value in changes:
            print(f'{target}: {digest(regular(target))[:12]} -> {digest(value)[:12]}')
        if not args.apply:
            print('Preflight only; no files changed.')
            return
        backup = Path('/var/lib/apx/backups') / (
            datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            + '-rofi-remove-choice')
        backup.mkdir(mode=0o700)
        manifest = []
        for index, (target, value) in enumerate(changes):
            metadata = target.stat()
            saved = backup / str(index)
            shutil.copy2(target, saved)
            manifest.append({'target': str(target), 'backup': str(saved),
                             'before': digest(regular(target)), 'after': digest(value),
                             'uid': metadata.st_uid, 'gid': metadata.st_gid,
                             'mode': metadata.st_mode & 0o777})
        (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        for (target, value), entry in zip(changes, manifest):
            descriptor, temporary = tempfile.mkstemp(prefix='.apx-rofi-remove-', dir=target.parent)
            try:
                with os.fdopen(descriptor, 'wb') as stream:
                    stream.write(value)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.chown(temporary, entry['uid'], entry['gid'])
                os.chmod(temporary, entry['mode'])
                os.replace(temporary, target)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            if digest(regular(target)) != entry['after']:
                raise RuntimeError(f'installed digest differs: {target}')
        print(f'Backup: {backup}')


if __name__ == '__main__':
    main()
