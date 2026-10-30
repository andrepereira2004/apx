#!/usr/bin/env python3
"""Deploy adaptive background reads to the authorized APX pilot."""
from pathlib import Path
import fcntl, importlib.util
if __name__ == '__main__':
    spec = importlib.util.spec_from_file_location('deploy', Path(__file__).with_name('deploy-controls-followup-20261020.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.AUDIT = module.REPO / 'audit/2026-10-24-quickshell-performance'
    module.AUDIT.mkdir(parents=True, exist_ok=True)
    module.transform.RELATIVES = ['quickshell/apx/ButtonOutline.qml', 'quickshell/apx/qmldir', 'quickshell/apx/Appearance.qml', 'quickshell/apx/BarButton.qml', 'quickshell/apx/MediaIsland.qml', 'quickshell/apx/MenuHover.qml', 'quickshell/apx/ControlTile.qml', 'quickshell/apx/RadioIconButton.qml', 'quickshell/apx/shell.qml', 'local/bin/apx-desktop-activity-v1']
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        module.main()
