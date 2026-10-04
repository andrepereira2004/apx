#!/usr/bin/env python3
"""Exact owner-requested stopped-workload config deployment; no packages/session switch."""
import datetime, fcntl, hashlib, json, os, re, shutil
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
BASE=Path('/var/lib/apx/environments')
SEED=Path('/usr/share/apx/config-seeds/environment-shell-v1')
assert Path('/etc/hostname').read_text().strip()=='apx-host'
assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
assert Path('/sys/class/dmi/id/board_name').read_text().strip()=='LNVNB161216'
assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
lock=open('/run/apx/machine-transition-v1.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert not Path('/run/apx/system-power-v1.reserved').exists()
names=['faculdade','hytale','minecraft','steam']
for name in names:
 r=json.loads((BASE/name/'registration.json').read_text());assert r['state']=='stopped' and r['role']=='graphical-base'
backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-environment-polish')
backup.mkdir(mode=0o700);manifest=[]
def write(p,data,owner=(0,0),mode=0o644):
 assert not p.is_symlink()
 existed=p.exists();st=p.stat() if existed else None
 entry=dict(target=str(p),existed=existed,uid=st.st_uid if st else owner[0],gid=st.st_gid if st else owner[1],mode=(st.st_mode&0o777) if st else mode)
 if existed:
  saved=backup/str(len(manifest));shutil.copy2(p,saved);entry['backup']=str(saved)
 manifest.append(entry);(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
 missing=[];parent=p.parent
 while not parent.exists():missing.append(parent);parent=parent.parent
 for parent in reversed(missing):
  parent.mkdir(mode=0o755 if owner==(0,0) else 0o700);os.chown(parent,*owner)
 p.write_bytes(data);os.chown(p,entry['uid'],entry['gid']);os.chmod(p,entry['mode'])
 entry['after']=hashlib.sha256(data).hexdigest()
source=REPO/'config/environment-shell-v1'
assets=['rofi/config.rasi','kitty/kitty.conf','apx/bashrc','local/bin/apx-sysinfo','gtk-3.0/settings.ini','gtk-3.0/gtk.css','hypr/hyprland.lua','hyprland/hyprland.conf']
data='/home/apx/.local/share/flatpak/exports/share:/var/lib/flatpak/exports/share:/usr/local/share:/usr/share'
rule='''\n-- A lone window needs no focus indicator. Count tiled and floating windows.
hl.window_rule({
    name = "apx-single-window-no-border",
    match = { workspace = "w[1]" },
    border_size = 0,
})
'''
for name in names:
 home=BASE/name/'home/apx';st=home.stat();owner=(st.st_uid,st.st_gid)
 p=home/'.config/hypr/hyprland.lua';s=p.read_text()
 s=re.sub(r'(active_border\s*=\s*)"rgba\([a-f0-9]+\)"',lambda m:m[1]+'"rgba(ffffffff)"',s,count=1)
 s=re.sub(r'(\n\s+border_size = )1,',r'\g<1>2,',s,count=1)
 if 'name = "apx-single-window-no-border"' not in s:s+=rule
 if 'hl.env("XDG_DATA_DIRS"' not in s:s+='\nhl.env("XDG_DATA_DIRS", "'+data+'")\n'
 write(p,s.encode(),owner,0o600)
 for rel in assets[:6]:
  p=home/('.local/'+rel[6:] if rel.startswith('local/') else '.config/'+rel)
  content=(source/rel).read_bytes()
  if rel=='gtk-3.0/settings.ini' and p.exists():
   import configparser,io
   cfg=configparser.ConfigParser(interpolation=None);cfg.optionxform=str;cfg.read(p);cfg.read(source/rel)
   stream=io.StringIO();cfg.write(stream,space_around_delimiters=False);content=stream.getvalue().encode()
  elif rel=='gtk-3.0/gtk.css' and p.exists():
   addition=content[content.index(b'/* Symbolic toolbar'):]
   content=p.read_bytes()+b'\n'+addition
  elif rel=='kitty/kitty.conf' and p.exists():
   content=p.read_bytes()+b'\n'+content
  write(p,content,owner,0o755 if rel.startswith('local/') else 0o600)
for rel in assets:write(SEED/rel,(source/rel).read_bytes(),mode=0o755 if rel.startswith('local/') else 0o644)
p=Path('/usr/lib/apx/apx-lab-runtime.py');text=p.read_text()
start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2
s=text[start:end]
for rel in assets:
 d=hashlib.sha256((source/rel).read_bytes()).hexdigest();pat=r'("'+re.escape(rel)+r'": ")[a-f0-9]+'
 if re.search(pat,s):s=re.sub(pat,lambda m:m[1]+d,s)
 else:s=s.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    "'+rel+'": "'+d+'",')
write(p,(text[:start]+s+text[end:]).encode())
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(backup)
