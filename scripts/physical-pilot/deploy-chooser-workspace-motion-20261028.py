#!/usr/bin/env python3
"""Deploy the reviewed chooser history and menu outline/motion changes."""
from pathlib import Path
import fcntl
import importlib.util

spec = importlib.util.spec_from_file_location(
    "deploy", Path(__file__).with_name("deploy-controls-followup-20261020.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.AUDIT = module.REPO / "audit/2026-10-28-chooser-workspace-motion"
module.transform.RELATIVES = [
    "local/lib/apx/chooser-places.c",
    "local/lib/apx/libchooser-places.so",
    "quickshell/apx/BarButton.qml",
    "quickshell/apx/ButtonOutline.qml",
    "quickshell/apx/ControlDashboard.qml",
    "quickshell/apx/MediaIsland.qml",
    "quickshell/apx/MenuHover.qml",
    "quickshell/apx/RadioIconButton.qml",
    "quickshell/apx/WorkspaceStrip.qml",
    "quickshell/apx/shell.qml",
]

with open("/run/apx/machine-transition-v1.lock", "a") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    module.main()
