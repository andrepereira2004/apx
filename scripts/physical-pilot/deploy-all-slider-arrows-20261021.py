#!/usr/bin/env python3
"""Apply keyboard slider controls to the fixed pilot using its reviewed adapter."""
from pathlib import Path
import fcntl
import importlib.util
if __name__ == '__main__':
    path = Path(__file__).with_name('deploy-controls-followup-20261020.py')
    spec = importlib.util.spec_from_file_location('slider_deploy', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.transform.RELATIVES = ['quickshell/apx/shell.qml', 'quickshell/apx/ControlSlider.qml']
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        module.main()
