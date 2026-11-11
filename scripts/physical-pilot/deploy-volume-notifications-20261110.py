#!/usr/bin/env python3
"""Install the reviewed volume and notification UI on the fixed APX pilot."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'config/environment-shell-v1'
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
RUNTIME = Path('/usr/lib/apx/apx-lab-runtime.py')
BACKUPS = Path('/var/lib/apx/backups')
NAMES = ('faculdade', 'hub', 'hytale', 'minecraft', 'steam')
ASSETS = (
    'local/bin/apx-audio-categories-v1',
    'local/bin/apx-desktop-activity-v1',
    'quickshell/apx/BounceMouseArea.qml',
    'quickshell/apx/NotificationInbox.qml',
    'quickshell/apx/NotificationMuteSelector.qml',
    'quickshell/apx/NotificationToasts.qml',
    'quickshell/apx/RadioIconButton.qml',
    'quickshell/apx/qmldir',
    'quickshell/apx/shell.qml',
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def identity():
    assert os.geteuid() == 0
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/sys_vendor').read_text().strip() == 'LENOVO'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert Path('/sys/class/dmi/id/board_name').read_text().strip() == 'LNVNB161216'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    active = json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
    assert active['name'] == 'faculdade' and active['role'] == 'graphical-base'
    assert set(path.name for path in Path('/var/lib/apx/environments').iterdir()
               if (path / 'registration.json').is_file()) == set(NAMES)


def home_path(name, relative):
    base = Path('/var/lib/apx/environments') / name / 'home/apx'
    return base / ('.local/' + relative.removeprefix('local/') if relative.startswith('local/')
                   else '.config/' + relative)


def plan():
    source_runtime = (REPO / 'scripts/virtual-lab/apx-lab-runtime.py').read_text()
    installed_runtime = RUNTIME.read_text()
    changes = {}
    for relative in ASSETS:
        data = (SOURCE / relative).read_bytes()
        if relative.startswith('quickshell/') or relative.startswith('local/'):
            targets = [SEED / relative] + [home_path(name, relative) for name in NAMES]
        else:
            raise AssertionError(relative)
        for target in targets:
            assert target.parent.is_dir() and not target.is_symlink(), target
            if not target.exists() or target.read_bytes() != data:
                changes[target] = data
        source_line = re.search(r'(?m)^    "' + re.escape(relative) + r'": "([a-f0-9]{64})",$', source_runtime)
        assert source_line and source_line.group(1) == digest(data), relative
        pattern = r'(?m)^    "' + re.escape(relative) + r'": "[a-f0-9]{64}",$'
        replacement = '    "' + relative + '": "' + digest(data) + '",'
        installed_runtime, count = re.subn(pattern, lambda _: replacement, installed_runtime)
        if count == 0:
            installed_runtime = installed_runtime.replace('ENVIRONMENT_SHELL_ASSETS = {',
                'ENVIRONMENT_SHELL_ASSETS = {\n' + replacement, 1)
        else:
            assert count == 1, relative
    # Preserve the already installed update helper. Its repository candidate
    # differs from the seed, and copying it would change package operations.
    legacy = 'local/bin/apx-environment-update-v1'
    legacy_digest = digest((SEED / legacy).read_bytes())
    installed_runtime, count = re.subn(
        r'(?m)^(    "' + re.escape(legacy) + r'": ")[a-f0-9]{64}(",)$',
        lambda match: match.group(1) + legacy_digest + match.group(2), installed_runtime)
    assert count == 1
    if RUNTIME.read_text() != installed_runtime:
        changes[RUNTIME] = installed_runtime.encode()
    return changes


def atomic(path, data, mode, uid, gid):
    assert not path.is_symlink(), path
    fd, temporary = tempfile.mkstemp(prefix='.apx-volume-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.chown(temporary, uid, gid)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def install(changes):
    backup = BACKUPS / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-volume-notifications')
    backup.mkdir(mode=0o700)
    inventory = []
    for path, data in changes.items():
        existed = path.exists()
        stat = path.stat() if existed else path.parent.stat()
        mode = stat.st_mode & 0o777 if existed else (0o755 if '/bin/' in str(path) else 0o644)
        uid, gid = (stat.st_uid, stat.st_gid)
        if '/var/lib/apx/environments/' in str(path):
            uid = gid = 1000
        saved = backup / str(path).lstrip('/')
        saved.parent.mkdir(parents=True, exist_ok=True)
        if existed:
            shutil.copy2(path, saved)
        inventory.append(dict(path=str(path), existed=existed, mode=mode, uid=uid, gid=gid,
                              before=digest(path.read_bytes()) if existed else None, after=digest(data)))
    (backup / 'inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    for item in sorted(inventory, key=lambda entry: entry['path'].endswith('/shell.qml')):
        path = Path(item['path'])
        atomic(path, changes[path], item['mode'], item['uid'], item['gid'])
        assert digest(path.read_bytes()) == item['after']
    # The entry point reloads after all imported components are in place.
    home_path('faculdade', 'quickshell/apx/shell.qml').touch()
    print(backup)
    print('Installed', len(inventory), 'files')


def rollback(backup):
    assert backup.parent == BACKUPS and backup.name.endswith('-volume-notifications')
    inventory = json.loads((backup / 'inventory.json').read_text())
    for item in sorted(inventory, key=lambda entry: entry['path'].endswith('/shell.qml')):
        path = Path(item['path'])
        assert digest(path.read_bytes()) == item['after'], path
        if item['existed']:
            atomic(path, (backup / str(path).lstrip('/')).read_bytes(), item['mode'], item['uid'], item['gid'])
        else:
            path.unlink()
    home_path('faculdade', 'quickshell/apx/shell.qml').touch()
    print('Restored', backup)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('plan', 'install', 'rollback'))
    parser.add_argument('backup', nargs='?')
    args = parser.parse_args()
    identity()
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.action == 'rollback':
            assert args.backup
            rollback(Path(args.backup).resolve())
            return
        changes = plan()
        if args.action == 'plan':
            print(json.dumps([str(path) for path in changes], indent=2))
        elif changes:
            install(changes)
        else:
            print('Already installed')


if __name__ == '__main__':
    main()
