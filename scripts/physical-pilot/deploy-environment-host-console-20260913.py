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
backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-environment-host-console')
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
assets=['local/bin/apx-host-console-open','local/bin/apx-host-console-terminal','hypr/hyprland.lua','local/share/icons/APX-Graphite/scalable/places/user-desktop.svg']
for name in names:
 home=BASE/name/'home/apx';st=home.stat();owner=(st.st_uid,st.st_gid)
 for rel in assets:
  if rel=='hypr/hyprland.lua':continue # Existing Super+H is already routed through QuickShell.
  target=home/('.local/'+rel[6:] if rel.startswith('local/') else '.config/'+rel)
  write(target,(source/rel).read_bytes(),owner,0o755 if rel.startswith('local/bin/') else 0o600)
for rel in assets:write(SEED/rel,(source/rel).read_bytes(),mode=0o755 if rel.startswith('local/bin/') else 0o644)
for p in [REPO/'scripts/virtual-lab/apx-lab-runtime.py',Path('/usr/lib/apx/apx-lab-runtime.py')]:
 text=p.read_text();start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2;s=text[start:end]
 for rel in assets:
  d=hashlib.sha256((source/rel).read_bytes()).hexdigest();pat=r'("'+re.escape(rel)+r'": ")[a-f0-9]+'
  if re.search(pat,s):s=re.sub(pat,lambda m:m[1]+d,s)
  else:s=s.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    "'+rel+'": "'+d+'",')
 write(p,(text[:start]+s+text[end:]).encode())
for name in ['apx-environment-host-console-v1.py','apx-host-console-v1.py','apx-host-console-client-v1.py','apx-graphical-environment-v1.py']:
 write(Path('/usr/lib/apx')/name,(REPO/'scripts/physical-pilot'/name).read_bytes(),mode=0o755)
unit='apx-environment-host-console-v1.service'
write(Path('/etc/systemd/system')/unit,(REPO/'config/systemd'/unit).read_bytes())
p=Path('/etc/systemd/system/multi-user.target.wants')/unit
assert not p.exists() and not p.is_symlink()
manifest.append(dict(target=str(p),existed=False,after_symlink='../'+unit,uid=0,gid=0,mode=0o777))
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
p.symlink_to('../'+unit)
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2));print(backup)
