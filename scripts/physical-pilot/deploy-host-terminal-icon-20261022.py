#!/usr/bin/env python3
"""Deploy the owner's Host-terminal icon without altering terminal behavior."""
from pathlib import Path
import fcntl
import importlib.util

if __name__ == '__main__':
    path = Path(__file__).with_name('deploy-controls-followup-20261020.py')
    spec = importlib.util.spec_from_file_location('host_terminal_icon', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.AUDIT = module.REPO / 'audit/2026-10-22-support-cleanup'
    module.AUDIT.mkdir(parents=True, exist_ok=True)
    module.transform.RELATIVES = [
        'local/bin/apx-window-apps-v1',
        'local/share/applications/apx-terminal.desktop',
        'local/share/icons/APX-Graphite/scalable/devices/apx-host-terminal.svg',
    ]
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        module.main()
