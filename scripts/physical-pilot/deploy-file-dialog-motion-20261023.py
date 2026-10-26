#!/usr/bin/env python3
"""Enable soft file-dialog entrances on the fixed disposable pilot."""
from pathlib import Path
import fcntl
import importlib.util

if __name__ == '__main__':
    spec = importlib.util.spec_from_file_location('dialog_motion', Path(__file__).with_name('deploy-controls-followup-20261020.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.AUDIT = module.REPO / 'audit/2026-10-23-file-dialog-motion'
    module.AUDIT.mkdir(parents=True, exist_ok=True)
    module.transform.RELATIVES = ['hypr/hyprland.lua']
    def transform(rel, text):
        # Preserve each Environment's unrelated compositor customization.
        for name in ['apx-thunar-modal-dialogs', 'apx-portal-file-dialogs']:
            start = text.index('    name = "' + name + '"')
            end = text.index('\n})', start)
            block = text[start:end].replace('    no_anim = true,', '    no_anim = false,\n    animation = "popin 94%",')
            text = text[:start] + block + text[end:]
        text = text.replace('speed = 4.79, spring = "easy"', 'speed = 2.8, bezier = "apxMenuOutCubic"')
        text = text.replace('speed = 2.8, spring = "apxSoftWindowOpen"', 'speed = 2.8, bezier = "apxMenuOutCubic"')
        text = text.replace('-- A lone window needs no focus indicator. Count tiled and floating windows.', '-- Floating dialogs must not change the border or geometry of the tiled parent.')
        text = text.replace('match = { workspace = "w[1]" },', 'match = { float = false, workspace = "w[tv1]" },', 1)
        return text
    module.transform.transform = staticmethod(transform)
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        module.main()
