#!/usr/bin/env python3
"""Install the bounded return-helper repair on the two identity-matched Windows."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[2]
RELEASE = Path('/usr/share/apx/native-v3-enabled.json')
PARTS = {'p3': '099c31d8-313a-4aba-b0e0-2b59502c9674',
         'p5': 'eddf4dba-7748-5ad6-a640-c9af195f5e1e'}


def require(value, message):
    if not value:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    require(os.geteuid() == 0 and Path('/etc/hostname').read_text().strip() == 'apx-host', 'Host differs')
    require(Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU', 'hardware differs')
    require(Path('/sys/class/block/nvme0n1/device/serial').read_text().strip() == 'S4DYNX0R253702', 'SSD differs')
    for path in ('/var/lib/apx/native-environments/pending-v3.json', '/run/apx/environment-management-v1.lock'):
        require(not Path(path).exists(), 'native or management operation pending')
    spec = importlib.util.spec_from_file_location('helper', REPO/'scripts/physical-pilot/apx-native-boot-runner-v1.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    firmware = helper.checked(('efibootmgr',), 'firmware unavailable')
    require('BootCurrent: 0005' in firmware and 'BootOrder: 0005,' in firmware and 'BootNext:' not in firmware, 'firmware differs')
    release = json.loads(RELEASE.read_text())
    for name, expected in release['files'].items():
        require(digest(Path(name)) == expected, 'release differs: ' + name)
    relative = {'APX-ReturnToHub.ps1': 'ProgramData/APX/ReturnToHub/APX-ReturnToHub.ps1',
                'README.txt': 'ProgramData/APX/ReturnToHub/README.txt'}
    for part, uuid in PARTS.items():
        device = Path('/dev/nvme0n1'+part)
        require(helper.block_value(device, 'PARTUUID').lower() == uuid, 'partition differs')
        require(helper.run(('findmnt', '-rn', '-S', str(device))).returncode != 0, 'Windows already mounted')
        report = helper.checked(('ntfsinfo', '-m', str(device)), 'NTFS not clean')
        require('Restart state: CLEAN' in report and 'Volume Flags: 0x0000' in report, 'NTFS journal differs')
        with helper.mounted_read_only(device, 'ntfs3') as root:
            helper.validate_hardware_and_return(root)
    backup = Path('/var/lib/apx/backups')/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-windows-return')
    backup.mkdir(mode=0o700)
    host = {Path('/usr/lib/apx')/name: REPO/'scripts/physical-pilot'/name for name in
            ('apx-native-boot-runner-v1.py', 'apx-native-lifecycle-v3.py', 'apx-native-windows-lifecycle-finalize-v1.py')}
    for name in relative:
        host[Path('/usr/share/apx/native-windows-lifecycle-v1/return')/name] = REPO/'config/native-windows-return-v1'/name
    host[RELEASE] = None
    for index, target in enumerate(host):
        require(target.is_file() and not target.is_symlink(), 'Host target differs')
        shutil.copy2(target, backup/('host-'+str(index)))
    changed = []
    inventory = []
    try:
        for part in PARTS:
            with helper.mounted_read_only(Path('/dev/nvme0n1'+part), 'ntfs3') as root:
                for name, rel in relative.items():
                    shutil.copy2(root/rel, backup/(part+'-'+name))
            # No force/recovery flags: refuse a dirty or hibernated Windows.
            import tempfile
            root = Path(tempfile.mkdtemp(prefix='apx-return-repair-', dir='/run'))
            try:
                helper.checked(('mount','-t','ntfs3','-o','rw,nosuid,nodev,noexec','/dev/nvme0n1'+part,str(root)), 'Windows write mount refused')
                try:
                    changed.append(part)
                    for name, rel in relative.items():
                        target = root/rel
                        source = REPO/'config/native-windows-return-v1'/name
                        require(not target.is_symlink(), 'Windows target differs')
                        target.write_bytes(source.read_bytes())
                        require(digest(target) == digest(source), 'Windows helper copy differs')
                        inventory.append({'partition':part,'path':rel,'sha256':digest(target)})
                    helper.checked(('sync',), 'sync failed')
                finally:
                    helper.checked(('umount',str(root)), 'unmount failed')
            finally:
                root.rmdir()
        for target, source in host.items():
            if source:
                target.write_bytes(source.read_bytes())
                require(digest(target) == digest(source), 'Host copy differs')
                inventory.append({'path':str(target),'sha256':digest(target)})
        for name in release['files']:
            release['files'][name] = digest(Path(name))
        RELEASE.write_text(json.dumps(release, sort_keys=True, separators=(',',':'))+'\n')
        (backup/'inventory.json').write_text(json.dumps(inventory, indent=2)+'\n')
        for part in PARTS:
            with helper.mounted_read_only(Path('/dev/nvme0n1'+part), 'ntfs3') as root:
                helper.validate_hardware_and_return(root)
                for name, rel in relative.items():
                    require(digest(root/rel) == digest(REPO/'config/native-windows-return-v1'/name), 'read-only verification differs')
        require(helper.checked(('efibootmgr',), 'firmware unavailable') == firmware, 'firmware changed')
    except Exception:
        for index, target in enumerate(host):
            shutil.copy2(backup/('host-'+str(index)), target)
        for part in reversed(changed):
            import tempfile
            root = Path(tempfile.mkdtemp(prefix='apx-return-rollback-',dir='/run'))
            try:
                helper.checked(('mount','-t','ntfs3','-o','rw,nosuid,nodev,noexec','/dev/nvme0n1'+part,str(root)), 'rollback mount failed')
                try:
                    for name, rel in relative.items():
                        (root/rel).write_bytes((backup/(part+'-'+name)).read_bytes())
                    helper.checked(('sync',), 'rollback sync failed')
                finally:
                    helper.checked(('umount',str(root)), 'rollback unmount failed')
            finally:
                root.rmdir()
        raise
    print('Return helpers installed and verified; backup: '+str(backup))


if __name__ == '__main__':
    main()
