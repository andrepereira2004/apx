#!/usr/bin/env python3
"""Enable Num Lock in each independent pilot configuration and the seed."""
from pathlib import Path
import fcntl
import importlib.util
import re
spec = importlib.util.spec_from_file_location("deploy", Path(__file__).with_name("deploy-controls-followup-20261020.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.AUDIT = m.REPO / "audit/2026-10-25-numlock"
m.AUDIT.mkdir(exist_ok=True)
m.transform.RELATIVES = ["local/bin/apx-numlock-state-v1", "hypr/hyprland.lua", "hyprland/hyprland.conf"]
def transform(rel, text):
    if rel == "local/bin/apx-numlock-state-v1":
        return (m.SOURCE / rel).read_text()
    if rel.endswith(".lua"):
        text = re.sub(r"(?m)^        numlock_by_default = (?:true|false),\n", "", text)
        anchor = "hl.config({\n    input = {"
        if "local rememberedNumLock" not in text:
            assert anchor in text
            text = text.replace(anchor, '''-- Local cache avoids broker calls on the compositor event loop.
local rememberedNumLock = false
local numLockFile = io.open("/home/apx/.config/hypr/apx-numlock-state", "r")
if numLockFile then
    rememberedNumLock = numLockFile:read("*l") == "true"
    numLockFile:close()
end

hl.config({
    input = {
        numlock_by_default = rememberedNumLock,''', 1)
        if 'apx-numlock-state-v1 restore' not in text:
            text = text.replace('  hl.exec_cmd("/home/apx/.local/bin/apx-input-startup-audit-v1")', '  hl.exec_cmd("/home/apx/.local/bin/apx-numlock-state-v1 restore")\n  hl.exec_cmd("/home/apx/.local/bin/apx-input-startup-audit-v1")', 1)
            text += '''
-- Save the owner's choice without consuming the normal Num Lock key event.
hl.bind("Num_Lock", hl.dsp.exec_cmd("/home/apx/.local/bin/apx-numlock-state-v1 save"), {
    release = true, non_consuming = true, locked = true, ignore_mods = true,
    submap_universal = true, dont_inhibit = true,
})
hl.on("config.reloaded", function ()
    hl.exec_cmd("/home/apx/.local/bin/apx-numlock-state-v1 restore")
end)
'''
        return text
    text = text.replace("bindrnligp =", "bindrnli =")
    text = re.sub(r"(?m)^    numlock_by_default = (?:true|false)\n", "", text)
    if 'apx-numlock-state-v1 restore' not in text:
        text += '\nexec = /home/apx/.local/bin/apx-numlock-state-v1 restore\nbindrnli = , Num_Lock, exec, /home/apx/.local/bin/apx-numlock-state-v1 save\n'
    return text
m.transform.transform = staticmethod(transform)
if __name__ == "__main__":
    with open("/run/apx/machine-transition-v1.lock", "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        m.main()
