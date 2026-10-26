#!/usr/bin/env python3
"""Deploy the owner-requested Apps/Files/System tabs on the fixed pilot."""
from pathlib import Path
import fcntl
import importlib.util

if __name__ == '__main__':
    path = Path(__file__).with_name('deploy-controls-followup-20261020.py')
    spec = importlib.util.spec_from_file_location('rofi_system', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.AUDIT = module.REPO / 'audit/2026-10-22-rofi-system'
    module.AUDIT.mkdir(parents=True, exist_ok=True)
    module.transform.RELATIVES = [
        'local/bin/apx-window-apps-v1', 'local/bin/apx-laptop-action-v1',
        'local/lib/rofi/apx-rofi-apps-v1.so', 'local/lib/rofi/apx-rofi-system-v1.so',
        'rofi/config.rasi', 'quickshell/apx/shell.qml',
    ]

    def transform(rel, text, target):
        if rel == 'quickshell/apx/shell.qml':
            updated = text.replace('"apps,files"', '"apps,files,system"')
        else:
            updated = (module.SOURCE / rel).read_text()
        if '/environments/hub/' in str(target) and rel in (
                'local/bin/apx-laptop-action-v1', 'quickshell/apx/shell.qml'):
            # Hub has the Files script, rather than the newer native Files module.
            updated = updated.replace('"apps,files,system"',
                '"apps,files:/home/apx/.local/bin/apx-rofi-files-v1,system"')
        return updated

    module.transform.transform_path = transform
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        module.main()
