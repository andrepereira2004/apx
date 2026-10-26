#!/usr/bin/env python3
"""Restore installed Hyprland default window animations."""
from pathlib import Path
import importlib.util, re, fcntl
spec = importlib.util.spec_from_file_location("deploy", Path(__file__).with_name("deploy-controls-followup-20261020.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.AUDIT = m.REPO / "audit/2026-10-26-window-reflow"
m.AUDIT.mkdir(exist_ok=True)
m.transform.RELATIVES = ["hypr/hyprland.lua"]
DEFAULT = (m.AUDIT / "installed-default.lua").read_text()
def transform(rel, text):
    def bounds(value):
        start = value.index('-- Default curves and animations,')
        last = re.search(r'^hl\.animation\(\{ leaf = "zoomFactor"[^\n]+', value, re.M)
        assert last
        return start, last.end()
    start, end = bounds(text)
    original_start, original_end = bounds(DEFAULT)
    original = DEFAULT[original_start:original_end]
    baseline = (m.AUDIT / "before-conversation.lua").read_text()
    base_start, base_end = bounds(baseline)
    block = baseline[base_start:base_end]
    for leaf in ("windows", "windowsIn", "windowsOut", "fadeIn", "fadeOut", "fade"):
        pattern = r'^hl\.animation\(\{ leaf = "' + leaf + r'",[^\n]+$'
        factory = re.search(pattern, original, re.M)
        block, count = re.subn(pattern, lambda match: factory[0], block, flags=re.M)
        assert count == 1
    block = re.sub(r'^hl\.animation\(\{ leaf = "windowsMove",[^\n]+\n', '', block, flags=re.M)
    text = text[:start] + block + text[end:]
    def clean_rule(match):
        return re.sub(r'^    (?:animation|no_anim) = [^\n]+\n', '', match[0], flags=re.M)
    return re.sub(r'hl\.window_rule\(\{.*?\n\}\)', clean_rule, text, flags=re.S)
m.transform.transform = staticmethod(transform)
if __name__ == "__main__":
    with open("/run/apx/machine-transition-v1.lock", "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        m.main()
