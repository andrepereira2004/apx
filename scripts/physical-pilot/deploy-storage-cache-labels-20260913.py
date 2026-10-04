#!/usr/bin/env python3
"""Bounded owner-requested pilot repair; preserves live bind-mounted inodes."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

REPO = Path('/root/apx-host-development-mode-v1/apx')
assert Path('/etc/hostname').read_text().strip() == 'apx-host'
assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
assert Path('/sys/class/dmi/id/board_name').read_text().strip() == 'LNVNB161216'
assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-storage-cache-labels')
backup.mkdir(mode=0o700)
shell = (REPO / 'config/environment-shell-v1/quickshell/apx/shell.qml').read_bytes()
sha = hashlib.sha256(shell).hexdigest()
targets = [(Path('/var/lib/apx/environments') / name / 'home/apx/.config/quickshell/apx/shell.qml', shell, None) for name in ['hub','faculdade','hytale','minecraft','steam']]
targets.append((Path('/usr/share/apx/config-seeds/environment-shell-v1/quickshell/apx/shell.qml'), shell, None))
runtime = Path('/usr/lib/apx/apx-lab-runtime.py')
content = re.sub(r'("quickshell/apx/shell.qml": ")[a-f0-9]+', lambda m: m[1]+sha, runtime.read_text()).encode()
targets.append((runtime, content, None))
targets.append((Path('/usr/lib/apx/apx-environment-storage-runner-v1.py'), (REPO / 'scripts/physical-pilot/apx-environment-storage-runner-v1.py').read_bytes(), 0o755))
for suffix in ['service','timer']:
    name = 'apx-environment-storage-v1.'+suffix
    targets.append((Path('/etc/systemd/system') / name, (REPO / 'config/systemd' / name).read_bytes(), 0o644))
manifest = []
for i, (target, content, new_mode) in enumerate(targets):
    assert not target.is_symlink()
    if target.exists():
        info = target.stat()
        saved = backup / str(i)
        shutil.copy2(target, saved)
        entry = dict(target=str(target), backup=str(saved), uid=info.st_uid, gid=info.st_gid, mode=info.st_mode & 0o777, before=hashlib.sha256(target.read_bytes()).hexdigest())
    else:
        assert new_mode is not None
        entry = dict(target=str(target), backup=None, uid=0, gid=0, mode=new_mode, before=None)
    manifest.append(entry)
(backup / 'manifest.json').write_text(json.dumps(manifest, indent=2))
for entry, (target, content, _) in zip(manifest, targets):
    with target.open('wb') as stream:
        stream.write(content)
    os.chown(target, entry['uid'], entry['gid'])
    os.chmod(target, entry['mode'])
    entry['after'] = hashlib.sha256(target.read_bytes()).hexdigest()
(backup / 'manifest.json').write_text(json.dumps(manifest, indent=2))
subprocess.run(['systemctl','daemon-reload'], check=True)
subprocess.run(['systemctl','start','apx-environment-storage-v1.service'], check=True)
subprocess.run(['systemctl','enable','--now','apx-environment-storage-v1.timer'], check=True)
print(backup)
