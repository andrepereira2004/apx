#!/usr/bin/env python3
"""Plan/apply the owner-selected Brave-only popup scaling workaround in Faculdade."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--scale', type=int, choices=(100, 125, 135, 150), default=150)
    args = parser.parse_args()
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert Path('/sys/class/dmi/id/board_name').read_text().strip() == 'LNVNB161216'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    environment = Path('/var/lib/apx/environments/faculdade')
    registration = json.loads((environment / 'registration.json').read_text())
    assert registration['name'] == 'faculdade'
    assert registration['role'] == 'graphical-base'
    target = environment / 'home/apx/.config/brave-flags.conf'
    assert target.is_file() and not target.is_symlink()
    before = target.read_bytes()
    lines = before.decode().splitlines()
    scale_lines = [line for line in lines if '--force-device-scale-factor' in line and not line.lstrip().startswith('#')]
    assert len(scale_lines) <= 1, 'Multiple browser scale overrides; review required'
    approved = {'--force-device-scale-factor=0.9', '--force-device-scale-factor=0.6666666666666666', '--force-device-scale-factor=0.8333333333333334'}
    assert not scale_lines or scale_lines[0] in approved, 'Unexpected browser scale override; review required'
    if args.scale == 150:
        annotation = '# Owner-selected Bitwarden popup fit: Brave-only UI scale compensation.'
        after = ''.join(line for line in before.decode().splitlines(keepends=True)
                        if line.rstrip('\r\n') not in scale_lines and line.rstrip('\r\n') != annotation).encode()
    else:
        factors = {100: '0.6666666666666666', 125: '0.8333333333333334', 135: '0.9'}
        desired = '--force-device-scale-factor=' + factors[args.scale]
        if scale_lines:
            after = before.decode().replace(scale_lines[0], desired, 1).encode()
        else:
            after = before.rstrip(b'\n') + b'\n# Owner-selected Bitwarden popup fit: Brave-only UI scale compensation.\n' + desired.encode() + b'\n'
    print(f'Faculdade only: Brave effective scale {args.scale}%; compositor scale unchanged.')
    print('Requires closing and reopening Brave; no browser restart is performed by this helper.')
    if not args.apply:
        print('Plan only: no files changed.')
        return
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/var/lib/apx/backups') / (stamp + '-brave-bitwarden-popup-scale')
    backup.mkdir(mode=0o700)
    shutil.copy2(target, backup / 'brave-flags.conf')
    metadata = target.stat()
    descriptor, name = tempfile.mkstemp(prefix='.apx-bitwarden-', dir=target.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(after)
            stream.flush()
            os.fsync(stream.fileno())
        os.chown(name, metadata.st_uid, metadata.st_gid)
        os.chmod(name, metadata.st_mode & 0o777)
        os.replace(name, target)
    finally:
        Path(name).unlink(missing_ok=True)
    assert target.read_bytes() == after
    (backup / 'manifest.json').write_text(json.dumps({'target': str(target), 'before': hashlib.sha256(before).hexdigest(), 'after': hashlib.sha256(after).hexdigest()}, indent=2) + '\n')
    print(backup)


if __name__ == '__main__':
    main()
