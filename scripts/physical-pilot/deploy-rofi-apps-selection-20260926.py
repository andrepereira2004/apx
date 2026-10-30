#!/usr/bin/env python3
"""Install the bounded Rofi application-menu revision on the physical pilot."""

import argparse
import ast
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
BASE = Path('/var/lib/apx/environments')
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
SOURCE = REPO / 'config/environment-shell-v1'
RELS = ('rofi/config.rasi', 'quickshell/apx/shell.qml',
        'local/bin/apx-window-apps-v1', 'local/bin/apx-application-remove-v1',
        'local/libexec/apx-rofi-secondary-v1.so')
NAMES = ('faculdade', 'hytale', 'minecraft', 'steam')
BEFORE = {
    'rofi/config.rasi': '82d42171e326',
    'quickshell/apx/shell.qml': 'e2117d2ac740',
    'local/bin/apx-window-apps-v1': '11cc74822ab2',
    'local/bin/apx-application-remove-v1': '5d9a2f077813',
    'local/libexec/apx-rofi-secondary-v1.so': 'f713aa8ec87f',
}
LIVE_QML = '033d461204b9'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def home_target(name, rel):
    home = BASE / name / 'home/apx'
    return home / ('.' + rel if rel.startswith('local/') else '.config/' + rel)


def update_qml(data):
    text = data.decode()
    changes = (
        ('    function showPopup() {\n        popupOpenAnimation.stop()',
         '    function showPopup() {\n        if (environmentAppsProcess.running) environmentAppsProcess.running = false\n        popupOpenAnimation.stop()'),
        ('    function togglePopup(kind, target, keyboardRequested) {\n        if (!target) return',
         '    function togglePopup(kind, target, keyboardRequested) {\n        if (!target) return\n        if (environmentAppsProcess.running) environmentAppsProcess.running = false'),
        ('"-me-accept-entry", "MousePrimary", "-me-accept-custom", "MouseSecondary"',
         '"-me-accept-entry", "", "-me-accept-custom", "MousePrimary,MouseSecondary"'),
        ('            if (!environmentAppsProcess.running)\n                environmentAppsProcess.running = true\n        }\n\n        function toggleApplications()',
         '            if (root.popup.open) root.closePopup()\n            environmentAppsProcess.running = !environmentAppsProcess.running\n        }\n\n        function toggleApplications()'),
        ('onActivated: { if (!environmentAppsProcess.running) environmentAppsProcess.running = true }',
         'onActivated: root.openApplications()'),
    )
    for old, new in changes:
        if text.count(old) != 1:
            raise RuntimeError('QuickShell baseline differs at application-menu integration')
        text = text.replace(old, new, 1)
    return text.encode()


def update_runtime(path, values):
    text = path.read_text()
    start = text.index('ENVIRONMENT_SHELL_ASSETS = {')
    end = text.index('\n}', start) + 2
    assets = ast.literal_eval(text[start:end].split(' = ', 1)[1])
    if not set(values).issubset(assets):
        raise RuntimeError(f'runtime asset map differs: {path}')
    assets.update({rel: digest(data) for rel, data in values.items()})
    replacement = 'ENVIRONMENT_SHELL_ASSETS = ' + json.dumps(assets, indent=4, sort_keys=True)
    return (text[:start] + replacement + text[end:]).encode()


def checked(path, expected=None):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f'unsafe or missing file: {path}')
    data = path.read_bytes()
    if expected and not digest(data).startswith(expected):
        raise RuntimeError(f'baseline digest differs: {path}')
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if (Path('/etc/hostname').read_text().strip(),
            Path('/sys/class/dmi/id/product_name').read_text().strip(),
            Path('/sys/class/dmi/id/board_name').read_text().strip()) != ('apx-host', '82JU', 'LNVNB161216'):
        raise RuntimeError('physical Host identity differs')
    if 'profile=apx-physical-headless-pilot-v1' not in Path('/etc/apx-physical-pilot').read_text().splitlines():
        raise RuntimeError('physical pilot marker differs')
    lock = open('/run/apx/machine-transition-v1.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if Path('/run/apx/system-power-v1.reserved').exists():
        raise RuntimeError('system power transition reserved')
    planned = []
    seed_values = {}
    source_values = {rel: checked(SOURCE / rel) for rel in RELS}
    for rel in RELS:
        original = checked(SEED / rel, BEFORE[rel])
        seed_values[rel] = update_qml(original) if rel.endswith('shell.qml') else source_values[rel]
        planned.append((SEED / rel, seed_values[rel]))
    for name in NAMES:
        registration = json.loads((BASE / name / 'registration.json').read_text())
        if (registration.get('name'), registration.get('role'), registration.get('state')) not in (
                (name, 'graphical-base', 'running'), (name, 'graphical-base', 'stopped')):
            raise RuntimeError(f'Environment differs: {name}')
        for rel in RELS:
            target = home_target(name, rel)
            original = checked(target, LIVE_QML if rel.endswith('shell.qml') else BEFORE[rel])
            value = update_qml(original) if rel.endswith('shell.qml') else source_values[rel]
            planned.append((target, value))
    source_runtime = REPO / 'scripts/virtual-lab/apx-lab-runtime.py'
    installed_runtime = Path('/usr/lib/apx/apx-lab-runtime.py')
    checked(source_runtime)
    checked(installed_runtime)
    next_source_runtime = update_runtime(source_runtime, source_values)
    planned.append((source_runtime, next_source_runtime))
    planned.append((installed_runtime, update_runtime(installed_runtime, seed_values)))
    recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
    old = checked(recovery).decode()
    changed, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=[0-9a-f]{64}$',
                             'readonly RUNTIME_SHA256=' + digest(next_source_runtime), old)
    if count != 1:
        raise RuntimeError('recovery runtime pin differs')
    planned.append((recovery, changed.encode()))
    print(f'Validated {len(planned)} files for seed, four workloads and runtime pins')
    if not args.apply:
        return
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-rofi-apps-selection')
    backup.mkdir(mode=0o700)
    entries = []
    for index, (target, data) in enumerate(planned):
        metadata = target.stat()
        saved = backup / str(index)
        shutil.copy2(target, saved)
        entries.append({'target': str(target), 'backup': str(saved),
                        'uid': metadata.st_uid, 'gid': metadata.st_gid,
                        'mode': metadata.st_mode & 0o777,
                        'before': digest(target.read_bytes()), 'after': digest(data)})
    (backup / 'manifest.json').write_text(json.dumps(entries, indent=2) + '\n')
    for (target, data), entry in zip(planned, entries):
        descriptor, temporary = tempfile.mkstemp(prefix='.apx-apps-', dir=target.parent)
        try:
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.chown(temporary, entry['uid'], entry['gid'])
            os.chmod(temporary, entry['mode'])
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        if digest(target.read_bytes()) != entry['after']:
            raise RuntimeError(f'installed digest differs: {target}')
    print(backup)


if __name__ == '__main__':
    main()
