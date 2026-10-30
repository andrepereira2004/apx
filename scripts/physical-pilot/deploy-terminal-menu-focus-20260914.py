#!/usr/bin/env python3
"""Exact owner-requested terminal presentation and menu-focus deployment."""
import ast
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'config/environment-shell-v1'
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
BASE = Path('/var/lib/apx/environments')
RELS = ['kitty/kitty.conf', 'apx/bashrc', 'local/bin/apx-sysinfo', 'quickshell/apx/shell.qml']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert Path('/sys/class/dmi/id/board_name').read_text().strip() == 'LNVNB161216'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    lock = open('/run/apx/machine-transition-v1.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert not Path('/run/apx/system-power-v1.reserved').exists()
    planned = []
    for name in ['hub', 'faculdade', 'hytale', 'minecraft', 'steam']:
        env = BASE / name
        registration = json.loads((env / 'registration.json').read_text())
        assert registration['state'] in ('running', 'stopped')
        assert registration['role'] == ('hub' if name == 'hub' else 'graphical-base')
        for rel in RELS:
            p = env / 'home/apx' / ('.' + rel if rel.startswith('local/') else '.config/' + rel)
            before = p.read_bytes()
            expected = (SEED / rel).read_bytes()
            if name == 'hub' and rel in ('kitty/kitty.conf', 'local/bin/apx-sysinfo'):
                expected = (SOURCE / rel).read_bytes()  # Reviewed owner reference assets.
            if name != 'hub' and rel == 'kitty/kitty.conf':
                expected = expected.replace(b'font_family Cascadia Mono\n', b'') + b'\nfont_family Cascadia Mono\n'
            if name != 'hub' and rel == 'quickshell/apx/shell.qml':
                expected = expected.replace(b'(root.isHub ? 470 : 394)', b'(root.isHub ? 440 : 394)')
            assert before == expected, str(p)
            planned.append((p, (SOURCE / rel).read_bytes()))
    for rel in RELS:
        planned.append((SEED / rel, (SOURCE / rel).read_bytes()))
    for p in [REPO / 'scripts/virtual-lab/apx-lab-runtime.py', Path('/usr/lib/apx/apx-lab-runtime.py')]:
        text = p.read_text()
        start = text.index('ENVIRONMENT_SHELL_ASSETS = {')
        end = text.index('\n}', start) + 2
        assets = ast.literal_eval(text[start:end].split(' = ', 1)[1])
        for rel in RELS:
            assert assets[rel] == digest((SEED / rel).read_bytes())
            assets[rel] = digest((SOURCE / rel).read_bytes())
        text = text[:start] + 'ENVIRONMENT_SHELL_ASSETS = ' + json.dumps(assets, indent=4, sort_keys=True) + text[end:]
        planned.append((p, text.encode()))
    runtime = next(data for p, data in planned if p == REPO / 'scripts/virtual-lab/apx-lab-runtime.py')
    p = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
    text, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=.*$', 'readonly RUNTIME_SHA256=' + digest(runtime), p.read_text())
    assert count == 1
    planned.append((p, text.encode()))
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-terminal-menu-focus')
    backup.mkdir(mode=0o700)
    manifest = []
    for i, (p, data) in enumerate(planned):
        assert p.is_file() and not p.is_symlink()
        st = p.stat()
        saved = backup / str(i)
        shutil.copy2(p, saved)
        manifest.append(dict(target=str(p), backup=str(saved), uid=st.st_uid, gid=st.st_gid, mode=st.st_mode & 0o777, before=digest(p.read_bytes()), after=digest(data)))
    (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    for (p, data), entry in zip(planned, manifest):
        p.write_bytes(data)
        os.chown(p, entry['uid'], entry['gid'])
        os.chmod(p, entry['mode'])
        assert digest(p.read_bytes()) == entry['after']
    print(backup)


if __name__ == '__main__':
    main()
