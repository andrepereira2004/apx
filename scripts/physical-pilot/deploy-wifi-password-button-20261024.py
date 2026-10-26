#!/usr/bin/env python3
"""Deploy the compact Wi-Fi password toggle to the authorized pilot."""
from pathlib import Path
import fcntl, importlib.util
if __name__ == '__main__':
    spec = importlib.util.spec_from_file_location('deploy', Path(__file__).with_name('deploy-controls-followup-20261020.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.AUDIT = module.REPO / 'audit/2026-10-24-wifi-password-button'
    module.AUDIT.mkdir(parents=True, exist_ok=True)
    module.transform.RELATIVES = ['quickshell/apx/shell.qml']
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        module.main()
