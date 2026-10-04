#!/usr/bin/env python3
"""Bounded pilot deployment; preserves per-Environment Lua customizations."""
import ast
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'config/environment-shell-v1'
SEED=Path('/usr/share/apx/config-seeds/environment-shell-v1')
RELS=['quickshell/apx/shell.qml','local/bin/apx-laptop-action-v1','hypr/hyprland.lua']
def digest(data):return hashlib.sha256(data).hexdigest()

def main():
    assert Path('/etc/hostname').read_text().strip()=='apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
    assert Path('/sys/class/dmi/id/board_name').read_text().strip()=='LNVNB161216'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    lock=open('/run/apx/machine-transition-v1.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not Path('/run/apx/system-power-v1.reserved').exists()
    planned=[]
    lua=(SOURCE/'hypr/hyprland.lua').read_text()
    layout=lua[lua.index('-- An Environment-local choice'):lua.index('\n\n---------------------\n---- MY PROGRAMS ----')]
    shortcut='hl.bind("SUPER + CTRL + Home", hl.dsp.exec_cmd("/home/apx/.local/bin/apx-laptop-action-v1 display-home"))'
    for name in ['hub','faculdade','hytale','minecraft','steam']:
        env=Path('/var/lib/apx/environments')/name
        record=json.loads((env/'registration.json').read_text())
        assert record['state'] in ('running','stopped')
        for rel in RELS:
            target=env/'home/apx'/('.'+rel if rel.startswith('local/') else '.config/'+rel)
            data=(SOURCE/rel).read_bytes()
            if rel=='hypr/hyprland.lua':
                old=target.read_text()
                anchor='\n\n---------------------\n---- MY PROGRAMS ----'
                assert old.count(anchor)==1
                if 'apx-monitors.lua' not in old:
                    old=old.replace(anchor,'\n'+layout+anchor,1)
                anchor='local mainMod = "SUPER" -- Sets "Windows" key as main modifier'
                assert old.count(anchor)==1
                if shortcut not in old:
                    old=old.replace(anchor,anchor+'\n'+shortcut,1)
                for side in ('Left','Right'):
                    binding='hl.bind("SUPER + SHIFT + '+side+'", hl.dsp.exec_cmd("/home/apx/.local/bin/apx-laptop-action-v1 window-'+side.lower()+'"))'
                    if binding not in old:
                        old += '\n'+binding+'\n'
                data=old.encode()
            else:
                old=target.read_bytes()
                expected=(SEED/rel).read_bytes()
                if rel.endswith('shell.qml'):
                    old=old.replace(b'        exclusiveZone: 0\n        WlrLayershell.layer: WlrLayer.Overlay',b'        WlrLayershell.layer: WlrLayer.Overlay\n        exclusiveZone: 0')
                assert old==expected,str(target)
            planned.append((target,data))
    for rel in RELS:planned.append((SEED/rel,(SOURCE/rel).read_bytes()))
    for target in [REPO/'scripts/virtual-lab/apx-lab-runtime.py',Path('/usr/lib/apx/apx-lab-runtime.py')]:
        text=target.read_text();start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2
        assets=ast.literal_eval(text[start:end].split(' = ',1)[1])
        for rel in RELS:assets[rel]=digest((SOURCE/rel).read_bytes())
        planned.append((target,(text[:start]+'ENVIRONMENT_SHELL_ASSETS = '+json.dumps(assets,indent=4,sort_keys=True)+text[end:]).encode()))
    runtime=next(data for p,data in planned if p==REPO/'scripts/virtual-lab/apx-lab-runtime.py')
    target=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
    text,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=.*$','readonly RUNTIME_SHA256='+digest(runtime),target.read_text());assert count==1
    planned.append((target,text.encode()))
    for target,rel in [('/var/lib/apx/official-hub-v1/apx-official-hub-graphical-v1.py','apx-official-hub-graphical-v1.py'),('/usr/lib/apx/apx-external-input-bridge-v1.py','apx-external-input-bridge-v1.py')]:
        planned.append((Path(target),(REPO/'scripts/physical-pilot'/rel).read_bytes()))
    backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-input-monitors')
    backup.mkdir(mode=0o700);manifest=[]
    for i,(target,data) in enumerate(planned):
        assert target.is_file() and not target.is_symlink()
        info=target.stat();saved=backup/str(i);shutil.copy2(target,saved)
        manifest.append(dict(target=str(target),backup=str(saved),uid=info.st_uid,gid=info.st_gid,mode=info.st_mode&0o777,before=digest(target.read_bytes()),after=digest(data)))
    (backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
    for (target,data),record in zip(planned,manifest):
        target.write_bytes(data);os.chown(target,record['uid'],record['gid']);os.chmod(target,record['mode'])
    print(backup)
if __name__=='__main__':main()
