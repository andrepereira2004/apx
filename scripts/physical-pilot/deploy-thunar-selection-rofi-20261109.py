#!/usr/bin/env python3
"""Deploy Thunar selection navigation and chooser identity to the fixed APX pilot."""
from pathlib import Path
import datetime
import fcntl
import hashlib
import json
import os
import re
import shutil
import sys

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'config/environment-shell-v1'
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
RUNTIME = Path('/usr/lib/apx/apx-lab-runtime.py')
ENVIRONMENTS = Path('/var/lib/apx/environments')
BACKUPS = Path('/var/lib/apx/backups')
ASSETS = ('local/bin/apx-window-apps-v1', 'local/libexec/apx-thunar-chrome-v1.so')
OLD = {
    'local/bin/apx-window-apps-v1': 'b6a03566ee77e77cc478cb8c391b3927489f93633ad0ad1e0cf51e173d77f9cd',
    'local/libexec/apx-thunar-chrome-v1.so': 'dc9775ec71fef5c44f3bfcfffc351abb8acda4b18c546e387f9410ff6af6b6ec',
}
PREVIOUS_MODULE = 'bcdc30b61845d6ba6272b816fd57781594ed5ab8bc9a671a8466108a741d7724'
PREVIOUS_CTRL_ENTER_MODULE = 'a8cf0a54d6c6606c45870d2a1e7a5ffb6d0f919cdfc53826676603a928e36f2f'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def destination(home, rel):
    return home / '.local' / rel.removeprefix('local/')


def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    assert sys.argv[1:] in ([], ['--check'])

    homes = [root / 'home/apx' for root in sorted(ENVIRONMENTS.iterdir())
             if (root / 'registration.json').is_file()]
    assert {home.parent.parent.name for home in homes} == {'hub', 'faculdade', 'hytale', 'minecraft', 'steam'}
    planned = {}
    new = {rel: (SOURCE / rel).read_bytes() for rel in ASSETS}
    for rel in ASSETS:
        assert digest(new[rel]) != OLD[rel]
        paths = [SEED / rel] + [destination(home, rel) for home in homes]
        for path in paths:
            assert path.is_file() and not path.is_symlink(), path
            current = digest(path.read_bytes())
            assert current in (OLD[rel], PREVIOUS_MODULE, PREVIOUS_CTRL_ENTER_MODULE,
                               digest(new[rel])), (path, current)
            if current != digest(new[rel]):
                planned[path] = new[rel]

    text = RUNTIME.read_text()
    updated = text
    for rel in ASSETS:
        pattern = r'("' + re.escape(rel) + r'": ")[a-f0-9]{64}("[,])'
        updated, count = re.subn(pattern, lambda match: match[1] + digest(new[rel]) + match[2], updated)
        assert count == 1, rel
    # An older live runtime pin for bookmarks would reject the independent
    # seed before the new Thunar and Rofi assets could reach future homes.
    bookmarks = 'gtk-3.0/bookmarks'
    bookmark_path = SEED / bookmarks
    assert bookmark_path.is_file() and not bookmark_path.is_symlink()
    pattern = r'("' + re.escape(bookmarks) + r'": ")[a-f0-9]{64}("[,])'
    updated, count = re.subn(pattern, lambda match: match[1] + digest(bookmark_path.read_bytes()) + match[2], updated)
    assert count == 1, bookmarks
    assert text != updated or not planned
    if text != updated:
        planned[RUNTIME] = updated.encode()

    if sys.argv[1:] == ['--check']:
        print(json.dumps({'homes': [str(home) for home in homes],
                          'planned': [str(path) for path in planned]}, indent=2))
        return
    if not planned:
        print('Already installed')
        return

    backup = BACKUPS / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
                        + '-thunar-selection-rofi')
    backup.mkdir(mode=0o700)
    inventory = []
    for path, data in planned.items():
        st = path.stat()
        saved = backup / path.relative_to('/')
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, saved)
        inventory.append({'path': str(path), 'before': digest(path.read_bytes()),
                          'after': digest(data), 'mode': st.st_mode & 0o777,
                          'uid': st.st_uid, 'gid': st.st_gid})
    (backup / 'inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    for item in inventory:
        path = Path(item['path'])
        temporary = path.with_name(path.name + '.apx-selection-new')
        temporary.write_bytes(planned[path])
        os.chmod(temporary, item['mode'])
        os.chown(temporary, item['uid'], item['gid'])
        os.replace(temporary, path)
        assert digest(path.read_bytes()) == item['after'], path
    print(backup)
    print('Verified', len(inventory), 'files')


if __name__ == '__main__':
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        main()
