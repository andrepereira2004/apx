#!/usr/bin/env python3
"""Align workload overlay fade with the resident menu duration and easing."""
import datetime
import fcntl
import hashlib
import os
from pathlib import Path
import re
import shutil

REPO = Path(__file__).resolve().parents[2]
ASSETS = ('hypr/hyprland.lua',)
CHANGES = {'hl.animation({ leaf = "layersIn",      enabled = true,  speed = 4,    bezier = "easeOutQuint", style = "fade" })': 'hl.animation({ leaf = "layersIn",      enabled = true,  speed = 1.6,  bezier = "apxMenuOutCubic", style = "fade" })', 'hl.animation({ leaf = "layersOut",     enabled = true,  speed = 1.5,  bezier = "linear",       style = "fade" })': 'hl.animation({ leaf = "layersOut",     enabled = true,  speed = 1.2,  bezier = "linear",       style = "fade" })', 'hl.animation({ leaf = "fadeLayersIn",  enabled = true,  speed = 1.79, bezier = "almostLinear" })': 'hl.animation({ leaf = "fadeLayersIn",  enabled = true,  speed = 1.6,  bezier = "apxMenuOutCubic" })', 'hl.animation({ leaf = "fadeLayersOut", enabled = true,  speed = 1.39, bezier = "almostLinear" })': 'hl.animation({ leaf = "fadeLayersOut", enabled = true,  speed = 1.2,  bezier = "linear" })'}
CURVE_ANCHOR = 'hl.curve("quick",          { type = "bezier", points = { {0.15, 0},    {0.1, 1}     } })'
CURVE_INSERT = '-- Overlay fade matches the 160ms OutCubic QuickShell menu transition.\nhl.curve("apxMenuOutCubic", { type = "bezier", points = { {0.215, 0.61}, {0.355, 1} } })'
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')


def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        planned = {}
        for target in [SEED / 'hypr/hyprland.lua'] + [Path('/var/lib/apx/environments') / name / 'home/apx/.config/hypr/hyprland.lua' for name in ('hytale', 'faculdade', 'minecraft', 'steam')]:
            original = target.read_text()
            if 'hl.curve("apxMenuOutCubic"' not in original:
                assert original.count(CURVE_ANCHOR) == 1
                original = original.replace(CURVE_ANCHOR, CURVE_ANCHOR + '\n' + CURVE_INSERT)
            for old, new in CHANGES.items():
                assert original.count(old) + original.count(new) == 1
                original = original.replace(old, new)
            planned[target] = original.encode()
        for runtime in (REPO / 'scripts/virtual-lab/apx-lab-runtime.py', Path('/usr/lib/apx/apx-lab-runtime.py')):
            original = runtime.read_text()
            start = original.index('ENVIRONMENT_SHELL_ASSETS = {')
            end = original.index('\n}', start) + 2
            block = original[start:end]
            for rel in ASSETS:
                value = (REPO / 'config/environment-shell-v1' / rel).read_bytes() if runtime == REPO / 'scripts/virtual-lab/apx-lab-runtime.py' else planned[SEED / rel]
                digest = hashlib.sha256(value).hexdigest()
                block, count = re.subn(r'("' + re.escape(rel) + r'": ")[a-f0-9]{64}("[,])',
                                      lambda m: m[1] + digest + m[2], block)
                assert count == 1
            planned[runtime] = (original[:start] + block + original[end:]).encode()
        recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
        text, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$',
                             'readonly RUNTIME_SHA256=' + hashlib.sha256(planned[REPO / 'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(), recovery.read_text())
        assert count == 1
        planned[recovery] = text.encode()
        backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-rofi-menu-animation')
        backup.mkdir(mode=0o700)
        for target in planned:
            assert target.is_file() and not target.is_symlink()
            saved = backup / str(target).lstrip('/')
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
        for target, data in planned.items():
            metadata = target.stat()
            temporary = target.with_name(target.name + '.rofi-animation-tmp')
            temporary.write_bytes(data)
            os.chown(temporary, metadata.st_uid, metadata.st_gid)
            os.chmod(temporary, metadata.st_mode & 0o777)
            os.replace(temporary, target)
            assert target.read_bytes() == data
        print(backup)


if __name__ == '__main__':
    main()
