#!/usr/bin/env python3
"""Apply the Control Centre palette to Rofi on the fixed disposable pilot."""
from pathlib import Path
import fcntl
import importlib.util
if __name__ == '__main__':
    path = Path(__file__).with_name('deploy-controls-followup-20261020.py')
    spec = importlib.util.spec_from_file_location('rofi_style', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.AUDIT = module.REPO / 'audit/2026-10-22-inbox-camera'
    module.transform.RELATIVES = ['quickshell/apx/MediaIsland.qml', 'quickshell/apx/shell.qml', 'quickshell/apx/Appearance.qml', 'quickshell/apx/ControlDashboard.qml', 'quickshell/apx/ActivityPanel.qml', 'quickshell/apx/DesktopActivity.qml', 'quickshell/apx/CameraIndicator.qml', 'quickshell/apx/NotificationInbox.qml', 'quickshell/apx/NotificationGroups.js', 'quickshell/apx/qmldir', 'local/bin/apx-microphone-activity-v1', 'local/bin/apx-desktop-activity-v1']
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        module.main()
