#!/usr/bin/env python3
"""Deploy the minimal lock presentation using the fixed pilot adapter."""
from pathlib import Path
import fcntl
import importlib.util

spec = importlib.util.spec_from_file_location("deploy", Path(__file__).with_name("deploy-controls-followup-20261020.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.AUDIT = m.REPO / "audit/2026-10-25-minimal-lock"
m.AUDIT.mkdir(exist_ok=True)
m.transform.RELATIVES = ["hypr/hyprlock.conf", "local/bin/apx-lock-date-v1"]
if __name__ == "__main__":
    with open("/run/apx/machine-transition-v1.lock", "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        m.main()
