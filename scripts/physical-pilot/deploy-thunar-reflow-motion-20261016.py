#!/usr/bin/env python3
"""Align tiled window reflow with the accepted entrance without changing Rofi."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil
REPO=Path(__file__).resolve().parents[2]
REL='hypr/hyprland.lua'

def update(text):
    line='hl.animation({ leaf = "windowsMove", enabled = true, speed = 1.6, bezier = "apxMenuOutCubic" })'
    if line in text:return text
    assert 'hl.curve("apxMenuOutCubic"' in text
    assert 'leaf = "windowsMove"' not in text
    pattern=r'(hl\.animation\(\{ leaf = "windowsIn",[^\n]*\}\))'
    text,count=re.subn(pattern,lambda m:m[1]+'\n-- Keep tiled layout reflow in step with window entrances; avoid the inherited spring.\n'+line,text)
    assert count==1
    return text

def main():
    assert Path('/etc/hostname').read_text().strip()=='apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
    source=REPO/'config/environment-shell-v1'/REL;seed=Path('/usr/share/apx/config-seeds/environment-shell-v1')/REL
    paths=[source,seed]+list(Path('/var/lib/apx/environments').glob('*/home/apx/.config/'+REL))
    planned={p:update(p.read_text()).encode() for p in paths}
    for runtime,asset in [(REPO/'scripts/virtual-lab/apx-lab-runtime.py',source),(Path('/usr/lib/apx/apx-lab-runtime.py'),seed)]:
        text,n=re.subn(r'("hypr/hyprland.lua": ")[a-f0-9]{64}("[,])',lambda m:m[1]+hashlib.sha256(planned[asset]).hexdigest()+m[2],runtime.read_text());assert n==1
        planned[runtime]=text.encode()
    recovery=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
    text,n=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+hashlib.sha256(planned[REPO/'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(),recovery.read_text());assert n==1
    planned[recovery]=text.encode()
    planned={p:d for p,d in planned.items() if p.read_bytes()!=d}
    if not planned:print('Tiled reflow motion already installed.');return
    backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-thunar-reflow-motion')
    inventory=[]
    for p,data in planned.items():
        assert not p.is_symlink()
        saved=backup/str(p).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,saved)
        metadata=p.stat();temporary=p.with_name(p.name+'.motion-tmp');temporary.write_bytes(data)
        os.chmod(temporary,metadata.st_mode&0o777);os.chown(temporary,metadata.st_uid,metadata.st_gid);os.replace(temporary,p)
        inventory.append({'path':str(p),'sha256':hashlib.sha256(data).hexdigest()})
    (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(backup)

if __name__=='__main__':main()
