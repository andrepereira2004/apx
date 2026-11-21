#!/usr/bin/env python3
"""Apply one hash-reviewed, non-rebooting pilot repair plan. Never deletes Windows."""
import argparse
import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import time

REPO = Path(__file__).resolve().parents[2]
NATIVE = Path('/var/lib/apx/native-environments')
MANIFEST = Path('/usr/share/apx/native-v3-enabled.json')
RELATIVES = {
    'APX-ReturnToHub.ps1': 'ProgramData/APX/ReturnToHub/APX-ReturnToHub.ps1',
    'APX-ReturnToHub.vbs': 'ProgramData/Microsoft/Windows/Start Menu/Programs/Startup/APX-ReturnToHub.vbs',
    'README.txt': 'ProgramData/APX/ReturnToHub/README.txt',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise RuntimeError(message)


def command(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True,
                          env={'PATH': '/usr/bin', 'LC_ALL': 'C'}, timeout=30).stdout


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def atomic(path, data, mode):
    descriptor, temporary = tempfile.mkstemp(prefix='.'+path.name, dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as output:
            os.fchmod(output.fileno(), mode)
            output.write(data); output.flush(); os.fsync(output.fileno())
        os.replace(temporary, path)
        fd = os.open(path.parent, os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        Path(temporary).unlink(missing_ok=True)


def clean_guest(part, expected):
    device = '/dev/nvme0n1p' + str(part)
    require(command('blkid', '-p', '-s', 'PART_ENTRY_UUID', '-o', 'value', device).strip().lower() == expected,
            'Windows partition identity changed')
    require(subprocess.run(['findmnt','-rn','-S',device], capture_output=True).returncode == 1,
            'Windows is already mounted')
    info = command('ntfsinfo', '-m', device)
    require('Restart state: CLEAN' in info and 'Volume Flags: 0x0000' in info,
            'Windows NTFS journal is not clean')
    # Read only the hibernation signature; do not copy the large hiberfil.
    probe = subprocess.Popen(['ntfscat',device,'/hiberfil.sys'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        signature = probe.stdout.read(4)
    finally:
        probe.stdout.close()
        if probe.poll() is None: probe.terminate()
        probe.wait(timeout=5)
    require(signature.lower() not in {b'hibr', b'wake'}, 'Windows is hibernated')



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    require(sha(args.plan) == args.sha256, 'deployment plan changed')
    plan = json.loads(args.plan.read_bytes())
    require(os.geteuid() == 0 and Path('/etc/hostname').read_text().strip() == 'apx-host', 'Host differs')
    require(Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU', 'hardware differs')
    require(Path('/sys/class/block/nvme0n1/device/serial').read_text().strip() == 'S4DYNX0R253702', 'SSD differs')
    require(not (NATIVE/'pending-v3.json').exists() and not Path('/run/apx/environment-management-v1.lock').exists(),
            'native/management operation pending')
    table = json.loads(command('sfdisk','--json','/dev/nvme0n1'))['partitiontable']
    require(table == plan['layout'], 'reviewed GPT changed')
    firmware = command('efibootmgr','-v')
    require('BootCurrent: 0005\n' in firmware and 'BootOrder: 0005,' in firmware and 'BootNext:' not in firmware,
            'Linux boot authority changed')
    require(sha(MANIFEST) == plan['manifest_before'], 'manifest changed')
    release = json.loads(MANIFEST.read_bytes())
    native = load(REPO/'src/apx_native_hub_v3.py', 'native_release')
    require(set(release['files']) == native.CRITICAL, 'manifest file set changed')
    for name, expected in plan['release_before'].items():
        require(sha(Path(name)) == expected, 'installed release changed: '+name)
    for item in plan['host']:
        target, source = Path(item['target']), REPO/item['source']
        require(target.is_file() and not target.is_symlink() and sha(target) == item['before'], 'Host target changed')
        require(sha(source) == item['after'], 'reviewed Host source changed')
    for name, expected in plan['guest_sources'].items():
        require(sha(REPO/'config/native-windows-return-v1'/name) == expected, 'reviewed guest source changed')
    checkpoint_path = NATIVE/'slot-layout-v3.json'
    require(not checkpoint_path.exists(), 'checkpoint already exists')
    helper = load(REPO/'scripts/physical-pilot/apx-native-boot-runner-v1.py', 'windows_helpers')
    # All guests must pass before any change. Never use force/recovery mounts.
    for part, record in plan['guests'].items():
        clean_guest(int(part), record['partuuid'])
        with helper.mounted_read_only(Path('/dev/nvme0n1p'+part), 'ntfs3') as root:
            for name, relative in RELATIVES.items():
                path = root/relative
                require(path.is_file() and not path.is_symlink() and sha(path) == record['files'][name], 'guest file changed')
    backup = Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-windows-return-slot')
    backup.mkdir(mode=0o700)
    shutil.copy2(args.plan, backup/'deployment-plan.json')
    saved = {}
    for item in plan['host'] + [{'target': str(MANIFEST)}]:
        path = Path(item['target']); destination = backup/str(path).lstrip('/')
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination); saved[path] = destination
    changed_guests = []
    broker_touched = False
    try:
        for part, record in plan['guests'].items():
            device = '/dev/nvme0n1p'+part
            clean_guest(int(part), record['partuuid'])
            with helper.mounted_read_only(Path(device), 'ntfs3') as root:
                directory = backup/('windows-p'+part); directory.mkdir()
                for name, relative in RELATIVES.items(): shutil.copy2(root/relative, directory/name)
            directory = Path(tempfile.mkdtemp(prefix='apx-windows-repair-', dir='/run'))
            try:
                command('mount','-t','ntfs3','-o','rw,nosuid,nodev,noexec',device,str(directory))
                try:
                    changed_guests.append(part)
                    for name, relative in RELATIVES.items():
                        path = directory/relative
                        require(not path.is_symlink() and sha(path) == record['files'][name], 'guest file changed before write')
                        path.write_bytes((REPO/'config/native-windows-return-v1'/name).read_bytes())
                    command('sync','-f',str(directory))
                finally: command('umount',str(directory))
            finally: directory.rmdir()
            with helper.mounted_read_only(Path(device), 'ntfs3') as root:
                for name, relative in RELATIVES.items():
                    require(sha(root/relative) == plan['guest_sources'][name], 'guest readback failed')
        for item in plan['host']:
            target = Path(item['target'])
            atomic(target, (REPO/item['source']).read_bytes(), stat.S_IMODE(target.stat().st_mode))
            require(sha(target) == item['after'], 'Host readback failed')
        atomic(checkpoint_path, (json.dumps(plan['checkpoint'],sort_keys=True)+'\n').encode(), 0o400)
        # Only hashes bound to reviewed plan sources or exact preflight bytes.
        new_release = dict(release, files=dict(plan['release_after']))
        for name, expected in new_release['files'].items(): require(sha(Path(name)) == expected, 'release readback failed')
        atomic(MANIFEST, (json.dumps(new_release,sort_keys=True)+'\n').encode(), 0o400)
        require(native.enabled(), 'release still disabled')
        require(command('efibootmgr','-v') == firmware, 'firmware changed unexpectedly')
        require(json.loads(command('sfdisk','--json','/dev/nvme0n1'))['partitiontable'] == table, 'GPT changed unexpectedly')
        endpoint = Path('/run/apx/environment-switch-v1.sock'); previous = endpoint.stat().st_ino
        broker_touched = True
        command('systemctl','restart','apx-environment-switch-v1.service')
        for _ in range(50):
            if endpoint.exists() and endpoint.stat().st_ino != previous: break
            time.sleep(.1)
        else: raise RuntimeError('broker socket unavailable')
        # Use the existing session socket-refresh mechanism; preserve its desktop.
        active = json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
        refresher = load(REPO/'scripts/physical-pilot/deploy-environment-icons-20261020.py', 'socket_refresher')
        fields = Path(f"/proc/{int(active['pid'])}/uid_map").read_text().split()
        require(len(fields) == 3 and fields[0] == '0' and fields[2] == '65536', 'active session uid map differs')
        translated = int(fields[1]) + 1000
        os.chown(endpoint, translated, translated); os.chmod(endpoint, 0o660)
        refresher.refresh_socket(int(active['pid']))
        command('systemctl','is-active','apx-environment-switch-v1.service')
    except Exception:
        for path, previous in saved.items(): shutil.copy2(previous, path)
        checkpoint_path.unlink(missing_ok=True)
        for part in reversed(changed_guests):
            directory = Path(tempfile.mkdtemp(prefix='apx-windows-rollback-',dir='/run'))
            try:
                command('mount','-t','ntfs3','-o','rw,nosuid,nodev,noexec','/dev/nvme0n1p'+part,str(directory))
                try:
                    for name, relative in RELATIVES.items(): (directory/relative).write_bytes((backup/('windows-p'+part)/name).read_bytes())
                    command('sync','-f',str(directory))
                finally: command('umount',str(directory))
            finally: directory.rmdir()
        if broker_touched:
            command('systemctl','restart','apx-environment-switch-v1.service')
            for _ in range(50):
                if Path('/run/apx/environment-switch-v1.sock').exists(): break
                time.sleep(.1)
            active = json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
            load(REPO/'scripts/physical-pilot/deploy-environment-icons-20261020.py', 'rollback_socket').refresh_socket(int(active['pid']))
        raise
    (backup/'complete.json').write_text(json.dumps({'firmware_unchanged':True,'gpt_unchanged':True,'windows_deleted':False,'guest_activation_pending':True})+'\n')
    print('Installed without reboot/delete; backup: '+str(backup))


if __name__ == '__main__':
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        main()
