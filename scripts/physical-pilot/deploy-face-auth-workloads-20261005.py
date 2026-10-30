#!/usr/bin/env python3
"""Owner-authorized workload-only enrollment; password remains available."""
import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'src'))
from apx_face_auth import install_identity, load_identity
BASE = Path('/var/lib/apx/environments')
ARTIFACTS = Path('/var/lib/apx/package-artifacts')
STAGING = Path('/var/lib/apx/backups/20261005-face-auth-staging/packages')
NAMES = ('faculdade', 'hytale', 'minecraft', 'steam')

def run(args, timeout=120):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError((result.stderr + result.stdout)[-3000:])
    return result.stdout

def active_machine(name, record):
    if record['state'] != 'running':
        return None
    machine = 'apx-g' + record['generation'][:7]
    assert run(['machinectl', 'show', machine, '-p', 'RootDirectory', '--value']).strip() == str(BASE/name/'root')
    return machine

def main():
    assert os.geteuid() == 0
    assert tuple(Path(p).read_text().strip() for p in ['/etc/hostname', '/sys/class/dmi/id/product_name', '/sys/class/dmi/id/board_name']) == ('apx-host', '82JU', 'LNVNB161216')
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert not Path('/run/apx/system-power-v1.reserved').exists()
        identity = load_identity(Path('/var/lib/apx/face-auth-v1'))
        assert identity
        records = {name: json.loads((BASE/name/'registration.json').read_text()) for name in NAMES}
        assert all(r['role'] == 'graphical-base' and r['state'] in ('running', 'stopped') for r in records.values())
        machines = {name: active_machine(name, record) for name, record in records.items()}
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        backup = Path('/var/lib/apx/backups')/(stamp+'-workload-face-auth')
        backup.mkdir(mode=0o700)
        packages = backup/'packages'
        shutil.copytree(STAGING, packages)
        packages.chmod(0o755)
        for path in packages.glob('*.pkg.tar.zst'):
            run(['pacman-key', '--verify', str(path)+'.sig', str(path)])
        local_artifacts = []
        for name in ('python-dlib', 'howdy-apx'):
            manifest = ARTIFACTS/(name+'-v1.json')
            record = json.loads(manifest.read_text())
            assert record['package'] == name and Path(record['filename']).name == record['filename']
            artifact = ARTIFACTS/record['filename']
            assert artifact.stat().st_uid == 0 and not artifact.is_symlink()
            assert hashlib.sha256(artifact.read_bytes()).hexdigest() == record['sha256']
            shutil.copy2(artifact, packages/artifact.name)
            local_artifacts.append(record)
        files = sorted(p.name for p in packages.glob('*.pkg.tar.zst'))
        (backup/'records.json').write_text(json.dumps(records, indent=2)+'\n')
        (backup/'local-artifacts.json').write_text(json.dumps(local_artifacts, indent=2)+'\n')
        for name in NAMES:
            assert not (BASE/name/'root/var/lib/pacman/db.lck').exists()
            run(['pacman', '--root', str(BASE/name/'root'), '-Up', '--print-format', '%n %v', *[str(packages/f) for f in files]])
        for name in NAMES:
            assert json.loads((BASE/name/'registration.json').read_text()) == records[name]
            snapshot = Path('/var/lib/apx/snapshots')/(name+'-'+records[name]['generation']+'-'+stamp)
            snapshot.mkdir(mode=0o700)
            for part in ('root', 'home'):
                run(['btrfs', 'subvolume', 'snapshot', '-r', str(BASE/name/part), str(snapshot/part)])
            shutil.copy2(BASE/name/'root/etc/pam.d/hyprlock', backup/(name+'-hyprlock.before'))
            machine = machines[name]
            if machine:
                location = '/run/apx-face-packages-'+stamp
                run(['machinectl', 'copy-to', machine, str(packages), location])
                prefix = ['systemd-run', '--machine='+machine, '--pipe', '--wait', '--quiet']
                output = run([*prefix, '/usr/bin/pacman', '-U', '--needed', '--noconfirm', *[location+'/'+f for f in files]], 600)
            else:
                prefix = ['systemd-nspawn', '--quiet', '--directory='+str(BASE/name/'root'), '--private-users=pick', '--private-users-ownership=chown', '--private-network', '--register=no']
                output = run([*prefix, '--bind-ro='+str(packages)+':/run/apx-face-packages', '/usr/bin/pacman', '-U', '--needed', '--noconfirm', *['/run/apx-face-packages/'+f for f in files]], 600)
            (backup/(name+'-packages.log')).write_text(output)
            # Import test before admitting facial PAM; a failure retains old PAM.
            run([*prefix, '/usr/bin/python', '-c', 'import cv2,dlib; print("Recognition libraries load")'])
            install_identity(BASE/name/'root', identity)
            if machine:
                user_prefix = [*prefix, '--uid=apx', '--gid=apx']
            else:
                user_prefix = [*prefix, '--uid=apx', '--bind-ro='+str(BASE/name/'home')+':/home:idmap']
            verification = run([*user_prefix, '/usr/bin/python', '-c',
                'import os,runpy; m=runpy.run_path("/home/apx/.local/bin/apx-face-auth-state-v1"); assert m["face_available"](); assert os.access("/etc/howdy/models/apx.dat",os.R_OK); assert not os.access("/etc/howdy/models/apx.dat",os.W_OK); print("Unprivileged lock: facial authentication available; model read-only")'])
            (backup/(name+'-verified.txt')).write_text(verification)
            if machine:
                run([*prefix, '/usr/bin/rm', '-r', '--', location])
            assert json.loads((BASE/name/'registration.json').read_text()) == records[name]
            print(name+': packages, PAM and private enrollment verified', flush=True)
        print(backup, flush=True)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        selected = tuple(dict.fromkeys(sys.argv[1:]))
        assert set(selected) <= set(NAMES)
        NAMES = selected
    main()
