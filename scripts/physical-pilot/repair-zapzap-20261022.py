#!/usr/bin/env python3
"""Restore a cached Qt6.11-compatible dependency set in fixed faculdade only."""
from pathlib import Path
import fcntl
import json
import subprocess

REPO = Path(__file__).resolve().parents[2]
PACKAGES = [
    'python-pyqt6-6.11.0-3-x86_64.pkg.tar.zst',
    'qt6-positioning-6.11.2-1-x86_64.pkg.tar.zst',
    'qt6-webchannel-6.11.2-1-x86_64.pkg.tar.zst',
    'qt6-webengine-6.11.2-1-x86_64.pkg.tar.zst',
]
if __name__ == '__main__':
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state = json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
        assert state['name'] == 'faculdade'
        root = Path('/var/lib/apx/environments/faculdade/root')
        assert not (root / 'var/lib/pacman/db.lck').exists()
        paths = ['/var/cache/pacman/pkg/' + p for p in PACKAGES]
        for p in paths:
            assert (root / p.lstrip('/')).is_file()
            assert (root / (p + '.sig').lstrip('/')).is_file()
        prefix = ['nsenter', '-t', str(int(state['pid'])), '-m', '-U', '-p', '-n', '--']
        version = subprocess.check_output(prefix + ['/usr/bin/pacman', '-Q', 'qt6-base'], text=True)
        assert version.strip() == 'qt6-base 6.11.2-3', version
        result = subprocess.run(prefix + ['/usr/bin/pacman', '-U', '--noconfirm', '--', *paths],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        out = REPO / 'audit/2026-10-22-zapzap-launch/repair.log'
        out.write_text(result.stdout)
        print(result.stdout)
        result.check_returncode()
