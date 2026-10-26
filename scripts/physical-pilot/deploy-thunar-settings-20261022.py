#!/usr/bin/env python3
"""Owner-requested native Files consistency and normalized mouse controls."""
from pathlib import Path
import fcntl
import importlib.util
import xml.etree.ElementTree as ET

if __name__ == '__main__':
    spec = importlib.util.spec_from_file_location('thunar_settings', Path(__file__).with_name('deploy-controls-followup-20261020.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.AUDIT = module.REPO / 'audit/2026-10-22-thunar-settings'
    module.AUDIT.mkdir(parents=True, exist_ok=True)
    module.transform.RELATIVES = ['local/bin/apx-settings', 'local/bin/apx-task-manager', 'local/share/apx/graphite-apps.css',
        'quickshell/apx/shell.qml', 'xfce4/xfconf/xfce-perchannel-xml/thunar.xml',
        'local/bin/apx-x11-density-v1', 'hypr/hyprland.lua']
    def transform(rel, text, path=None):
        if rel.endswith('/thunar.xml'):
            root = ET.fromstring(text)
            prop = root.find("./property[@name='last-separator-position']")
            if prop is None: prop = ET.SubElement(root, 'property', name='last-separator-position', type='int')
            prop.set('value', '219'); ET.indent(root)
            return ET.tostring(root, encoding='unicode') + '\n'
        return (module.SOURCE / rel).read_text()
    module.transform.transform = staticmethod(transform)
    module.transform.transform_path = staticmethod(transform)
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);module.main()
