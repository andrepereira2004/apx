#!/usr/bin/env python3
"""Install a Minecraft-only user launcher for NVIDIA in Hybrid mode."""

import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile


REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'config/environment-minecraft-v1'
BASE = Path('/var/lib/apx/environments/minecraft')
HOME = BASE / 'home/apx'
PAIRS = (
    ('local/bin/apx-minecraft-nvidia-v1', HOME / '.local/bin/apx-minecraft-nvidia-v1', 0o755),
    ('local/share/applications/minecraft-launcher.desktop',
     HOME / '.local/share/applications/minecraft-launcher.desktop', 0o644),
)
BASELINE_DESKTOP = '09006f33be0d4540dfb1838db00ec6c5d3a542e8c8c58c8374f4f85479222e3f'
BASELINE_WRAPPER = '222d66f4007168b7c3f6e78f2be98c4bba8d1cef19a4b5d9955980cf00112d27'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if (Path('/etc/hostname').read_text().strip(),
            Path('/sys/class/dmi/id/product_name').read_text().strip()) != ('apx-host', '82JU'):
        raise RuntimeError('Physical Host identity differs')
    if 'profile=apx-physical-headless-pilot-v1' not in Path('/etc/apx-physical-pilot').read_text().splitlines():
        raise RuntimeError('Physical pilot marker differs')
    lock = open('/run/apx/machine-transition-v1.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    registration = json.loads((BASE / 'registration.json').read_text())
    if (registration.get('name'), registration.get('role'), registration.get('state')) != (
            'minecraft', 'graphical-base', 'stopped'):
        raise RuntimeError('Minecraft Environment is not stopped')
    if digest((BASE / 'root/usr/share/applications/minecraft-launcher.desktop').read_bytes()) != BASELINE_DESKTOP:
        raise RuntimeError('Minecraft package desktop entry differs')
    if digest((BASE / 'root/usr/bin/minecraft-launcher.sh').read_bytes()) != BASELINE_WRAPPER:
        raise RuntimeError('Minecraft package launcher differs')
    if Path('/sys/module/nvidia/version').read_text().strip() != '610.43.03':
        raise RuntimeError('Host NVIDIA version differs')
    if os.readlink(BASE / 'root/usr/lib/libEGL_nvidia.so.0') != 'libEGL_nvidia.so.610.43.03':
        raise RuntimeError('Minecraft NVIDIA userspace differs')
    if b'APX_GPU_POLICY="$GPU_POLICY"' not in Path(
            '/var/lib/apx/official-hub-v1/apx-official-hub-session-v1.sh').read_bytes():
        raise RuntimeError('Graphical session lacks GPU policy marker')
    planned = []
    for relative, target, mode in PAIRS:
        source = SOURCE / relative
        if not source.is_file() or source.is_symlink() or target.exists() or target.is_symlink():
            raise RuntimeError(f'Minecraft launcher source or target differs: {relative}')
        planned.append((target, source.read_bytes(), mode))
    if b'Exec=/home/apx/.local/bin/apx-minecraft-nvidia-v1' not in planned[1][1]:
        raise RuntimeError('Minecraft desktop command differs')
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-minecraft-nvidia-launch')
    backup.mkdir(mode=0o700)
    owner = HOME.stat().st_uid
    group = HOME.stat().st_gid
    manifest = [{'target': str(path), 'before': 'absent', 'after': digest(data),
                 'uid': owner, 'gid': group, 'mode': mode} for path, data, mode in planned]
    (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for path, data, mode in planned:
        descriptor, temporary = tempfile.mkstemp(prefix='.apx-minecraft-nvidia-', dir=path.parent)
        try:
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.chown(temporary, owner, group)
            os.chmod(temporary, mode)
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        if digest(path.read_bytes()) != digest(data):
            raise RuntimeError(f'Minecraft launcher install verification failed: {path}')
    print(backup)


if __name__ == '__main__':
    main()
