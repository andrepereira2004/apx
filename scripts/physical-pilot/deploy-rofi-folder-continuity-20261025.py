#!/usr/bin/env python3
"""Deploy the native Files continuity fix using the bounded pilot installer."""
import fcntl,importlib.util
from pathlib import Path
path=Path(__file__).with_name('deploy-rofi-files-flicker-20261022.py')
spec=importlib.util.spec_from_file_location('files_installer',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.AUDIT=module.REPO/'audit/2026-10-25-rofi-folder-continuity'
if __name__=='__main__':
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        module.main()
