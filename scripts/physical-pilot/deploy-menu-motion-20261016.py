#!/usr/bin/env python3
"""Align window/layer entrances with the resident menu motion."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil
REPO=Path(__file__).resolve().parents[2]
REL='hypr/hyprland.lua'

def update(text):
    if 'name = "apx-rofi-menu-motion"' in text:return text
    curve='hl.curve("apxMenuOutCubic", { type = "bezier", points = { {0.215, 0.61}, {0.355, 1} } })'
    if 'hl.curve("apxMenuOutCubic"' not in text:
        anchor='-- Default springs'
        assert text.count(anchor)==1
        text=text.replace(anchor,'-- Match the QuickShell OutCubic menu entrance.\n'+curve+'\n\n'+anchor)
    motions={
        'windowsIn':(1.6,'popin 96%'),
        'windowsOut':(1.2,'popin 96%'),
        'fadeIn':(1.6,None), 'fadeOut':(1.2,None),
        'layersIn':(1.6,'fade'), 'layersOut':(1.2,'fade'),
        'fadeLayersIn':(1.6,None), 'fadeLayersOut':(1.2,None),
    }
    for leaf,(speed,style) in motions.items():
        replacement='hl.animation({ leaf = "'+leaf+'", enabled = true, speed = '+str(speed)+', bezier = "apxMenuOutCubic"'
        if style:replacement+=', style = "'+style+'"'
        replacement+=' })'
        text,count=re.subn(r'hl\.animation\(\{ leaf = "'+leaf+r'",[^\n]*\}\)',replacement,text)
        assert count==1,leaf
    pattern=r'-- File operations should not animate or resize the main file-manager tile\.\nhl.window_rule\(\{\n    name = "apx-thunar-no-animation",\n    match = \{ class = "\^\(thunar\|Thunar\|org\.xfce\.Thunar\)\$" \},\n    no_anim = true,\n    border_size = 2,\n\}\)'
    replacement='-- Main file-manager windows enter like the resident menus.\n-- Transient/progress dialogs retain their non-animated rules below.\nhl.window_rule({\n    name = "apx-thunar-menu-animation",\n    match = { class = "^(thunar|Thunar|org.xfce.Thunar)$" },\n    animation = "popin 96%",\n    border_size = 2,\n})\n\n-- Rofi is a full-screen transparent layer containing a centered card.\n-- Scale only that layer; resident QuickShell menus animate their own content.\nhl.layer_rule({\n    name = "apx-rofi-menu-motion",\n    match = { namespace = "^rofi$" },\n    animation = "popin 96%",\n})'
    text,count=re.subn(pattern,lambda _:replacement,text)
    assert count==1,'Thunar main-window animation rule missing'
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
    if not planned:print('Menu motion already installed.');return
    backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-menu-motion')
    inventory=[]
    for p,data in planned.items():
        assert not p.is_symlink()
        saved=backup/str(p).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,saved)
        metadata=p.stat();temporary=p.with_name(p.name+'.motion-tmp');temporary.write_bytes(data)
        os.chmod(temporary,metadata.st_mode&0o777);os.chown(temporary,metadata.st_uid,metadata.st_gid);os.replace(temporary,p)
        inventory.append({'path':str(p),'sha256':hashlib.sha256(data).hexdigest()})
    (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(backup)

if __name__=='__main__':main()
