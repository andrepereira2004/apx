#!/usr/bin/env python3
from pathlib import Path
import fcntl,importlib.util
spec=importlib.util.spec_from_file_location('deploy',Path(__file__).with_name('deploy-controls-followup-20261020.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.AUDIT=module.REPO/'audit/2026-10-26-control-greeting'
module.transform.RELATIVES=['quickshell/apx/ControlDashboard.qml']
with open('/run/apx/machine-transition-v1.lock','a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    module.main()
