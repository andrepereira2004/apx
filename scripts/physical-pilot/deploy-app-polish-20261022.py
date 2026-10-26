#!/usr/bin/env python3
"""Deploy owner-requested Graphite application styling and Settings controls."""
from pathlib import Path
import fcntl
import importlib.util
import os
import json
import sys

if __name__ == '__main__':
    spec = importlib.util.spec_from_file_location('app_polish', Path(__file__).with_name('deploy-controls-followup-20261020.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.AUDIT = module.REPO / 'audit/2026-10-22-app-polish'
    module.AUDIT.mkdir(parents=True, exist_ok=True)
    module.transform.RELATIVES = [
        'local/bin/apx-settings', 'local/bin/apx-task-manager',
        'local/share/apx/graphite-apps.css',
        'local/share/themes/APX-Graphite/gtk-3.0/gtk.css',
        'local/share/applications/xfce4-taskmanager.desktop',
        'hypr/hyprland.lua', 'hyprland/hyprland.conf',
        'hypr/apx-monitors.lua', 'local/bin/apx-laptop-action-v1',
        'quickshell/apx/shell.qml',
    ]
    def transform_path(rel, text, path):
        if rel == 'hypr/apx-monitors.lua':
            return text.replace('scale="auto"', 'scale=1.25')
        return (module.SOURCE / rel).read_text()
    module.transform.transform_path = staticmethod(transform_path)
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert Path('/etc/hostname').read_text().strip() == 'apx-host'
        assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
        if sys.argv[1:] == []:
            created = []
            bases = [module.SEED] + [d / 'home/apx' for d in Path('/var/lib/apx/environments').iterdir()
                     if (d / 'registration.json').is_file() and (d / 'home/apx/.config/quickshell/apx/shell.qml').is_file()]
            for base in bases:
                for rel in ['apx', 'themes/APX-Graphite/gtk-3.0']:
                    root = base / 'local/share' if base == module.SEED else base / '.local/share'
                    target = root / rel
                    pending = []
                    while not target.exists():
                        pending.append(target)
                        target = target.parent
                    stat = root.stat()
                    for directory in reversed(pending):
                        directory.mkdir(mode=0o755)
                        os.chown(directory, stat.st_uid, stat.st_gid)
                        created.append(str(directory))
            if created:
                (module.AUDIT / 'created-directories.json').write_text(json.dumps(created, indent=2) + '\n')
        module.main()
