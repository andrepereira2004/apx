#!/usr/bin/env python3
"""Return the APX launcher to Apps and Files without losing applications."""
from pathlib import Path
import fcntl
import importlib.util

spec = importlib.util.spec_from_file_location(
    "deploy", Path(__file__).with_name("deploy-controls-followup-20261020.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.AUDIT = module.REPO / "audit/2026-10-28-rofi-two-tabs"
module.AUDIT.mkdir(parents=True, exist_ok=True)
module.transform.RELATIVES = [
    "local/bin/apx-window-apps-v1",
    "local/bin/apx-laptop-action-v1",
    "rofi/config.rasi",
    "quickshell/apx/shell.qml",
]

with open("/run/apx/machine-transition-v1.lock", "a") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    module.main()
