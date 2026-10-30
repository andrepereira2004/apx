#!/usr/bin/env python3
"""Request NVIDIA for Hytale's Flatpak in hybrid mode, preserving its override."""

import os
from pathlib import Path
import shutil
import tempfile


OVERRIDE = Path('/var/lib/apx/environments/hytale/home/apx/.local/share/flatpak/overrides/com.hypixel.HytaleLauncher')
BACKUP = Path('/var/lib/apx/backups/20260927T-hytale-nvidia-offload/com.hypixel.HytaleLauncher')
EXPECTED = b'[Environment]\nGDK_BACKEND=wayland\n'
ADDITION = b'__NV_PRIME_RENDER_OFFLOAD=1\n__GLX_VENDOR_LIBRARY_NAME=nvidia\n'


def main():
    if os.uname().nodename != 'apx-host':
        raise SystemExit('Unexpected Host')
    if BACKUP.exists():
        raise SystemExit('Backup already exists')
    if OVERRIDE.read_bytes() != EXPECTED:
        raise SystemExit('Hytale Flatpak override differs')
    runtime = Path('/var/lib/apx/environments/hytale/home/apx/.local/share/flatpak/runtime/org.freedesktop.Platform.GL.nvidia-610-43-03')
    if not runtime.is_dir() or Path('/sys/module/nvidia/version').read_text().strip() != '610.43.03':
        raise SystemExit('NVIDIA Flatpak runtime or Host driver differs')
    stat = OVERRIDE.stat()
    BACKUP.parent.mkdir(parents=True, exist_ok=False)
    shutil.copy2(OVERRIDE, BACKUP)
    os.chown(BACKUP, stat.st_uid, stat.st_gid)
    if BACKUP.read_bytes() != EXPECTED:
        raise SystemExit('Backup verification failed')
    descriptor, temporary = tempfile.mkstemp(prefix='.hytale-nvidia-', dir=OVERRIDE.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(EXPECTED + ADDITION)
            stream.flush()
            os.fsync(stream.fileno())
        os.chown(temporary, stat.st_uid, stat.st_gid)
        os.chmod(temporary, stat.st_mode & 0o777)
        os.replace(temporary, OVERRIDE)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    if OVERRIDE.read_bytes() != EXPECTED + ADDITION:
        raise SystemExit('Installed override verification failed')
    print(f'Hytale NVIDIA offload requested; backup {BACKUP}')


if __name__ == '__main__':
    main()
