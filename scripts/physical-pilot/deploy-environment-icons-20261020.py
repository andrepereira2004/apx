#!/usr/bin/env python3
"""Migrate Hub-local icon choices to generation-bound Host metadata on fixed pilot."""
from pathlib import Path
import ctypes
import configparser
import datetime
import fcntl
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[2]
ENVIRONMENTS = Path('/var/lib/apx/environments')
AUDIT = REPO/'audit/2026-10-20-environment-icons'


def refresh_socket(pid):
    """Refresh only the active session's replaceable fallback socket mount."""
    target = Path(f'/proc/{pid}/root/run/apx/environment-switch-refresh-v1.sock')
    assert not target.is_symlink()
    prefix = ['nsenter', '-t', str(pid), '-m', '-U', '-p', '-r', '-w', '--']
    if target.exists() and target.stat().st_nlink == 0:
        subprocess.run(prefix + ['umount', '/run/apx/environment-switch-refresh-v1.sock'], check=True)
    if not target.exists(): target.touch(mode=0o600)
    libc = ctypes.CDLL(None, use_errno=True)
    fd = libc.syscall(428, -100, b'/run/apx/environment-switch-v1.sock', 1 | os.O_CLOEXEC)
    if fd < 0: raise OSError(ctypes.get_errno(), 'open_tree')
    try:
        program = 'import ctypes;libc=ctypes.CDLL(None,use_errno=True);r=libc.syscall(429,'+str(fd)+',b"",-100,b"/run/apx/environment-switch-refresh-v1.sock",4);assert r==0,(r,ctypes.get_errno())'
        subprocess.run(prefix + ['python', '-c', program], pass_fds=(fd,), check=True)
    finally:
        os.close(fd)


def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    assert sys.argv[1:] in ([], ['--check'])
    spec = importlib.util.spec_from_file_location('icon_contract', REPO/'src/apx_environment_switch_contract.py')
    contract = importlib.util.module_from_spec(spec); spec.loader.exec_module(contract)
    AUDIT.mkdir(exist_ok=True)
    planned = {}
    for source, target in [
        (REPO/'src/apx_environment_switch_contract.py', Path('/usr/lib/apx/apx_environment_switch_contract.py')),
        *[(REPO/'scripts/physical-pilot'/name, Path('/usr/lib/apx')/name) for name in
          ('apx-environment-switch-client-v1.py', 'apx-environment-metadata-runner-v1.py', 'apx-environment-switch-v1.py')],
    ]:
        assert target.is_file() and not target.is_symlink()
        if source.read_bytes() != target.read_bytes(): planned[target] = source.read_bytes()
    settings = configparser.ConfigParser(interpolation=None)
    settings.read(ENVIRONMENTS/'hub/home/apx/.config/apx-environment-icons.ini')
    encoded = settings.get('Environments', 'choices', fallback='{}')
    choices = json.loads(json.loads(encoded) if encoded.startswith('"') else encoded)
    migrated = []
    for key, icon in choices.items():
        name, generation = key.split(':')
        assert contract.NAME.fullmatch(name) and contract.GENERATION.fullmatch(generation) and icon in contract.ENVIRONMENT_ICONS
        candidates = [ENVIRONMENTS/name/'registration.json', Path('/var/lib/apx/native-environments/instances-v3')/(name+'.json'), Path('/var/lib/apx/native-environments')/(name+'.json')]
        if not any(p.is_file() and json.loads(p.read_text()).get('generation') == generation for p in candidates): continue
        target = ENVIRONMENTS/f'.icon-{name}-{generation}.json'
        # Migration never replaces a choice already saved by the new editor.
        if not target.exists(): planned[target] = (json.dumps(dict(name=name, generation=generation, icon=icon), sort_keys=True)+'\n').encode()
        migrated.append(dict(name=name, generation=generation, icon=icon))
    (AUDIT/'migration.json').write_text(json.dumps(migrated, indent=2)+'\n')
    if sys.argv[1:] == ['--check']:
        print('Pending Host files:', len(planned)); return
    backup = Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-environment-icons')
    backup.mkdir(); inventory = []
    for path, data in planned.items():
        existed = path.exists(); st = path.stat() if existed else None
        saved = backup/str(path).lstrip('/'); saved.parent.mkdir(parents=True, exist_ok=True)
        if existed: shutil.copy2(path, saved)
        inventory.append(dict(path=str(path), existed=existed, mode=st.st_mode & 0o777 if st else 0o600))
    # In-place helper updates preserve the read-only bind mounts in existing sessions.
    # The broker is then restarted to load the same contract as new clients.
    for path, data in planned.items():
        if path.exists():
            with path.open('wb') as out: out.write(data); out.flush(); os.fsync(out.fileno())
        else:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'wb') as out: out.write(data); out.flush(); os.fsync(out.fileno())
    (backup/'inventory.json').write_text(json.dumps(inventory, indent=2)+'\n')
    if planned:
        endpoint = Path('/run/apx/environment-switch-v1.sock')
        previous = endpoint.stat().st_ino
        subprocess.run(['systemctl', 'restart', 'apx-environment-switch-v1.service'], check=True)
        for attempt in range(50):
            if endpoint.exists() and endpoint.stat().st_ino != previous:
                break
            time.sleep(.1)
        else:
            raise RuntimeError('New switch broker socket did not become ready')

    for marker in ('active-graphical-environment-v1.json', 'official-hub-graphical-v1.json'):
        path = Path('/run/apx')/marker
        if path.is_file():
            state = json.loads(path.read_text())
            pid = int(state['pid'])
            if Path(f'/proc/{pid}/root/run/apx/environment-switch-v1.sock').exists():
                fields = Path(f'/proc/{pid}/uid_map').read_text().split()
                assert len(fields) == 3 and fields[0] == '0' and int(fields[2]) == 65536
                translated = int(fields[1]) + 1000
                os.chown('/run/apx/environment-switch-v1.sock', translated, translated)
                os.chmod('/run/apx/environment-switch-v1.sock', 0o660)
                refresh_socket(pid)
                break
    # Remove the obsolete traversal exception; private Hub directories stay private.
    acl = REPO/'audit/2026-10-20-environments-minimal/icon-directory-acls.before.txt'
    if acl.is_file(): subprocess.run(['setfacl', '-P', '--restore='+str(acl)], check=True)
    print(backup)


if __name__ == '__main__':
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        main()
