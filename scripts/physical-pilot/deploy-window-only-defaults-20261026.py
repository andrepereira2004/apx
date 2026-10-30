#!/usr/bin/env python3
"""Restore only ordinary window motion; leave shell/workspace motion untouched."""
from pathlib import Path
import re, fcntl, types
helper = Path(__file__).with_name('deploy-controls-followup-20261020.py')
m = types.ModuleType('bounded_deploy')
m.__file__ = str(helper)
code = helper.read_text().replace(" for home in homes:(home/'.config/quickshell/apx/shell.qml').touch()", " pass # No QuickShell reload for window-only changes.")
exec(compile(code, str(helper), 'exec'), m.__dict__)
m.AUDIT = m.REPO / 'audit/2026-10-26-window-only-defaults'
m.AUDIT.mkdir(exist_ok=True)
m.transform.RELATIVES = ['hypr/hyprland.lua']
REFERENCE = (m.AUDIT / 'reference-before-0845-rollback.lua').read_text()
def transform(rel, text):
    # Recover the exact historical window definitions requested by the owner.
    for leaf in ('windows', 'windowsIn', 'windowsOut', 'fadeIn', 'fadeOut', 'fade'):
        pattern = r'^hl\.animation\(\{ leaf = "' + leaf + r'",[^\n]+$'
        original = re.search(pattern, REFERENCE, re.M)
        assert original
        text, n = re.subn(pattern, lambda _: original[0], text, flags=re.M)
        assert n == 1
    text = re.sub(r'^hl\.animation\(\{ leaf = "windowsMove",[^\n]+\n', '', text, flags=re.M)
    curve = r'^hl\.curve\("easy"[^\n]+$'
    original = re.search(curve, REFERENCE, re.M)
    text, n = re.subn(curve, lambda _: original[0], text, flags=re.M)
    assert n == 1
    rule = r'hl\.window_rule\(\{\n    name = "apx-thunar-menu-animation",.*?\n\}\)'
    original = re.search(rule, REFERENCE, re.S)
    current = re.search(rule, text, re.S)
    assert original and current
    strip = lambda value: re.sub(r'^    animation = [^\n]+\n', '', value, flags=re.M)
    assert strip(original[0]) == strip(current[0]), 'Preserve all non-animation rule fields'
    text, n = re.subn(rule, lambda _: original[0], text, flags=re.S)
    assert n == 1
    return text
m.transform.transform = staticmethod(transform)
if __name__ == '__main__':
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        m.main()
