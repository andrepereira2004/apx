#!/usr/bin/env python3
"""Apply the Control Centre palette to Kitty and Thunar on the fixed disposable pilot."""
from pathlib import Path
import fcntl
import importlib.util
import re
if __name__ == '__main__':
    path = Path(__file__).with_name('deploy-controls-followup-20261020.py')
    spec = importlib.util.spec_from_file_location('terminal_files_style', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.AUDIT = module.REPO / 'audit/2026-10-22-terminal-files-style'
    module.transform.RELATIVES = ['kitty/kitty.conf', 'gtk-3.0/gtk.css', 'local/bin/apx-appearance-v1']
    def transform(rel, text):
        source = (module.SOURCE / rel).read_text()
        if rel == 'gtk-3.0/gtk.css':
            generated = re.search(r'/\* APX appearance override BEGIN \*/.*?/\* APX appearance override END \*/', text, re.S)
            if generated:
                source += '\n' + generated.group(0) + '\n'
        return source
    module.transform.transform = staticmethod(transform)
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        module.main()
