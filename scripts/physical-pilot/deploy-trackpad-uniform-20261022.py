#!/usr/bin/env python3
"""Persist owner-requested 35/100 trackpad cursor across all fixed pilot homes."""
from pathlib import Path
import fcntl
import importlib.util
if __name__ == '__main__':
    path = Path(__file__).with_name('deploy-controls-followup-20261020.py')
    spec = importlib.util.spec_from_file_location('trackpad_uniform', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.transform.RELATIVES = ['hypr/apx-trackpad-sensitivity.lua', 'local/bin/apx-trackpad-sensitivity-v1']
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        module.main()
