#!/usr/bin/env python3
"""Install the tested native Files module on the identity-pinned disposable pilot."""
import datetime, fcntl, hashlib, json, os, re, shutil, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
REL = 'local/lib/rofi/apx-rofi-files-v1.so'
HELPER = 'local/bin/apx-rofi-files-v1'
AUDIT = REPO / 'audit/2026-10-22-rofi-files-flicker'

def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    assert sys.argv[1:] in ([], ['--check'])
    artifact = AUDIT / 'apx-rofi-files-v1.so'
    data = artifact.read_bytes()
    assert data.startswith(b'\x7fELF')
    source = REPO / 'config/environment-shell-v1'
    seed = Path('/usr/share/apx/config-seeds/environment-shell-v1')
    helper_data = (source / HELPER).read_bytes()
    planned = {source / REL: data, seed / REL: data, seed / HELPER: helper_data}
    for env in sorted(Path('/var/lib/apx/environments').iterdir()):
        if (env / 'registration.json').is_file():
            path = env / 'home/apx/.local/lib/rofi/apx-rofi-files-v1.so'
            if env.name == 'hub':
                # Hub still uses its distinct legacy script-mode configuration.
                assert not path.exists(), path
                continue
            assert path.is_file(), path
            planned[path] = data
            planned[env / 'home/apx/.local/bin/apx-rofi-files-v1'] = helper_data
    for path in [REPO / 'scripts/virtual-lab/apx-lab-runtime.py', Path('/usr/lib/apx/apx-lab-runtime.py')]:
        text = path.read_text()
        for relative, value in [(REL, data), (HELPER, helper_data)]:
            value_digest = hashlib.sha256(value).hexdigest()
            text, n = re.subn(r'("' + re.escape(relative) + r'": ")[a-f0-9]{64}("[,])', lambda m: m[1] + value_digest + m[2], text)
            assert n == 1
        planned[path] = text.encode()
    recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
    runtime_digest = hashlib.sha256(planned[REPO / 'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest()
    text, n = re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$', 'readonly RUNTIME_SHA256=' + runtime_digest, recovery.read_text())
    assert n == 1
    planned[recovery] = text.encode()
    planned = {p: d for p, d in planned.items() if p.read_bytes() != d}
    for path in planned:
        assert path.is_file() and not path.is_symlink(), path
    (AUDIT / 'planned-paths.json').write_text(json.dumps(list(map(str, planned)), indent=2) + '\n')
    if sys.argv[1:] == ['--check'] or not planned:
        print('Pending:', len(planned)); return
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-rofi-files-flicker')
    backup.mkdir(mode=0o700)
    inventory = []
    for path, value in planned.items():
        stat = path.stat()
        dest = backup / str(path).lstrip('/')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        inventory.append(dict(path=str(path), mode=stat.st_mode & 0o777, uid=stat.st_uid, gid=stat.st_gid, before=hashlib.sha256(path.read_bytes()).hexdigest(), after=hashlib.sha256(value).hexdigest()))
    (backup / 'inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    for item in inventory:
        path = Path(item['path'])
        temp = path.with_name(path.name + '.rofi-flicker-tmp')
        temp.write_bytes(planned[path]); os.chmod(temp, item['mode']); os.chown(temp, item['uid'], item['gid'])
        os.replace(temp, path)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item['after']
    (AUDIT / 'backup.txt').write_text(str(backup) + '\n')
    print('Backup:', backup)
    print('Verified:', len(inventory))

if __name__ == '__main__':
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        main()
