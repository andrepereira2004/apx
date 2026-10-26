#!/usr/bin/env python3
"""Deploy native Electron scaling without changing monitor or browser scale."""
from pathlib import Path
import fcntl
import importlib.util

if __name__ == '__main__':
    spec = importlib.util.spec_from_file_location('native_scale_deploy', Path(__file__).with_name('deploy-controls-followup-20261020.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.AUDIT = module.REPO / 'audit/2026-10-23-native-scale'
    module.AUDIT.mkdir(parents=True, exist_ok=True)
    module.transform.RELATIVES = ['local/bin/apx-native-scale-v1', 'local/bin/apx-application-catalog-v1']
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        module.main()
