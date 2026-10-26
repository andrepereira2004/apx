#!/usr/bin/env python3
"""Deploy typed keyboard preference operations using the fixed broker adapter."""
import fcntl
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('broker_deploy', Path(__file__).with_name('deploy-radio-power-20261020.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.FILES = {target: source for target, source in m.FILES.items() if not target.endswith('apx-host-services-ui-v3.py')}
if __name__ == '__main__':
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        m.main()
