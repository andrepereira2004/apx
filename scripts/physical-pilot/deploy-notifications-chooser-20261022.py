#!/usr/bin/env python3
"""Apply the compact navigation icons to Thunar on the fixed disposable pilot."""
from pathlib import Path
import fcntl
import importlib.util
import re
import xml.etree.ElementTree as ET
if __name__ == '__main__':
    path = Path(__file__).with_name('deploy-controls-followup-20261020.py')
    spec = importlib.util.spec_from_file_location('terminal_files_style', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.AUDIT = module.REPO / 'audit/2026-10-22-notifications-chooser'
    module.transform.RELATIVES = ['quickshell/apx/ActivityPanel.qml', 'local/bin/apx-desktop-activity-v1', 'local/bin/apx-shell-v1', 'local/bin/apx-desktop-activation-v1', 'hypr/hyprland.lua', 'hyprland/hyprland.conf', 'gtk-3.0/gtk.css']
    def transform(rel, text):
        source = (module.SOURCE / rel).read_text()
        if rel == 'gtk-3.0/settings.ini':
            # Load only for Thunar, rather than from GTK's shared settings.
            lines = []
            for line in text.splitlines():
                if line.startswith('gtk-modules='):
                    values = [m for m in line.split('=', 1)[1].split(':')
                              if m and m != '/home/apx/.local/libexec/apx-thunar-chrome-v1.so']
                    if values: lines.append('gtk-modules=' + ':'.join(values))
                else:
                    lines.append(line)
            return '\n'.join(lines) + '\n'
        if rel.endswith('/thunar.xml'):
            root = ET.fromstring(text)
            prop = root.find("./property[@name='misc-small-toolbar-icons']")
            if prop is None:
                prop = ET.SubElement(root, 'property', name='misc-small-toolbar-icons', type='bool')
            prop.set('value', 'true')
            ET.indent(root)
            return ET.tostring(root, encoding='unicode') + '\n'
        if rel == 'gtk-3.0/gtk.css':
            generated = re.search(r'/\* APX appearance override BEGIN \*/.*?/\* APX appearance override END \*/', text, re.S)
            if generated:
                source += '\n' + generated.group(0) + '\n'
        return source
    module.transform.transform = staticmethod(transform)
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        module.main()
