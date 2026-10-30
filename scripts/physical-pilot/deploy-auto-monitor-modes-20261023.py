#!/usr/bin/env python3
"""Apply automatic maximum monitor modes to the fixed pilot, preserving layouts."""
from pathlib import Path
import fcntl
import importlib.util
import re

if __name__ == '__main__':
    spec = importlib.util.spec_from_file_location('auto_monitor_deploy', Path(__file__).with_name('deploy-controls-followup-20261020.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.AUDIT = module.REPO / 'audit/2026-10-23-auto-monitor-modes'
    module.AUDIT.mkdir(parents=True, exist_ok=True)
    module.transform.RELATIVES = ['hypr/apx-monitors.lua', 'hypr/hyprland.lua',
                                  'hyprland/hyprland.conf', 'local/bin/apx-laptop-action-v1']
    def transform_path(rel, text, path):
        if rel == 'hypr/apx-monitors.lua':
            # Keep output names, placement and scale local; remove fixed old modes.
            return re.sub(r'\bmode\s*=\s*"[^"]*"', 'mode="highres"', text)
        if rel == 'hypr/hyprland.lua':
            return re.sub(r'\bmode\s*=\s*"preferred"', 'mode = "highres"', text)
        if rel == 'hyprland/hyprland.conf':
            return re.sub(r'(?m)^(monitor\s*=\s*,\s*)preferred(\s*,)', r'\1highres\2', text)
        return text.replace('mode="preferred"', 'mode="highres"')
    module.transform.transform_path = staticmethod(transform_path)
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        module.main()
