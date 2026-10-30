#!/usr/bin/env python3
"""Deploy parallel unlock instructions and seed pins with the fixed pilot adapter."""
from pathlib import Path
import fcntl
import importlib.util
if __name__ == '__main__':
    path=Path(__file__).with_name('deploy-controls-followup-20261020.py')
    spec=importlib.util.spec_from_file_location('unlock_ui_deploy',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.AUDIT=module.REPO/'audit/2026-10-22-parallel-unlock'
    module.transform.RELATIVES=['hypr/hyprlock.conf','local/bin/apx-face-auth-state-v1']
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);module.main()
