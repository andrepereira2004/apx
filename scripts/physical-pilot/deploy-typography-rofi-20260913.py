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
names=['hub','faculdade','hytale','minecraft','steam']
for name in names:
 r=json.loads((BASE/name/'registration.json').read_text());assert r['state'] in ('running','stopped') and r['role'] in ('hub','graphical-base')
backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-typography-rofi')
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
rels=['rofi/config.rasi','fontconfig/fonts.conf','gtk-3.0/settings.ini','gtk-3.0/bookmarks','gtk-4.0/settings.ini','xfce4/xfconf/xfce-perchannel-xml/thunar.xml','Thunar/uca.xml','local/bin/apx-application-catalog-v1','local/bin/apx-application-remove-v1','local/bin/apx-desktop-activation-v1','local/bin/apx-laptop-action-v1','local/bin/apx-shell-v1','local/bin/apx-workspace-overview-v1']
qml=[str(p.relative_to(source)) for p in (source/'quickshell/apx').glob('*.qml') if 'font.family:' in p.read_text()]
for name in names:
 home=BASE/name/'home/apx';st=home.stat();owner=(st.st_uid,st.st_gid)
 home_alias=home.parent/'Home'
 if home_alias.exists() or home_alias.is_symlink():
  assert home_alias.is_symlink() and os.readlink(home_alias)=='apx'
 else:
  manifest.append(dict(target=str(home_alias),existed=False,after_symlink='apx'))
  home_alias.symlink_to('apx')
 for rel in rels:
  target=home/('.'+rel) if rel.startswith('local/') else home/'.config'/rel
  write(target,(source/rel).read_bytes(),owner,0o755 if rel.startswith('local/bin/') else 0o600)
 for rel in qml:
  target=home/'.config'/rel
  write(target,(source/rel).read_bytes(),owner,0o600)
 root=BASE/name/'root/etc/passwd'; original=root.read_text()
 updated=original.replace('apx:x:1000:1000:APX graphical Environment:/home/apx:/usr/bin/bash', 'apx:x:1000:1000:Home:/home/apx:/usr/bin/bash')
 if 'home:x:1000:1000:Home:/home/apx:/usr/bin/bash\n' not in updated:
  updated=updated.replace('apx:x:1000:1000:Home:/home/apx:/usr/bin/bash', 'home:x:1000:1000:Home:/home/apx:/usr/bin/bash\napx:x:1000:1000:Home:/home/apx:/usr/bin/bash')
 if updated != original: write(root,updated.encode(),(0,0),0o644)
for rel in rels+qml:write(SEED/rel,(source/rel).read_bytes(),mode=0o755 if rel.startswith('local/bin/') else 0o644)
for p in [REPO/'scripts/virtual-lab/apx-lab-runtime.py',Path('/usr/lib/apx/apx-lab-runtime.py')]:
 text=p.read_text();start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2
 import ast
 assets=ast.literal_eval(text[start:end].split(' = ',1)[1])
 for rel in rels+qml:assets[rel]=hashlib.sha256((source/rel).read_bytes()).hexdigest()
 text=text[:start]+'ENVIRONMENT_SHELL_ASSETS = '+json.dumps(assets,indent=4,sort_keys=True)+text[end:]
 write(p,text.encode())
p=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
s=re.sub(r'(?m)^readonly RUNTIME_SHA256=.*$', 'readonly RUNTIME_SHA256='+hashlib.sha256((REPO/'scripts/virtual-lab/apx-lab-runtime.py').read_bytes()).hexdigest(),p.read_text());write(p,s.encode())
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2));print(backup)
