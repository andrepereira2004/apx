#!/usr/bin/env python3
"""Synchronize the owner-requested Files-style Settings sidebar."""
from pathlib import Path
import importlib.util
import fcntl
spec = importlib.util.spec_from_file_location('deploy', Path(__file__).with_name('deploy-controls-followup-20261020.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.AUDIT = m.REPO / 'audit/2026-10-23-settings-sidebar'
m.AUDIT.mkdir(parents=True, exist_ok=True)
m.transform.RELATIVES = ['local/bin/apx-task-manager', 'local/bin/apx-settings', 'local/share/apx/graphite-apps.css']
with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    m.main()
