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
backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-desktop-compatibility')
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
assets=['local/bin/apx-desktop-activation-v1','local/bin/apx-shell-v1']
for name in names:
 home=BASE/name/'home/apx';st=home.stat();owner=(st.st_uid,st.st_gid)
 rel=assets[0];write(home/'.local/bin/apx-desktop-activation-v1',(source/rel).read_bytes(),owner,0o755)
 p=home/'.local/bin/apx-shell-v1';s=p.read_text()
 marker='# These are ordinary desktop facilities'
 addition=(source/'local/bin/apx-shell-v1').read_text().split('# Publish Wayland/X11')[1].split(marker)[0]
 assert marker in s and 'apx-desktop-activation-v1' not in s
 write(p,s.replace(marker,'# Publish Wayland/X11'+addition+marker,1).encode(),owner,0o755)
 root=BASE/name/'root';st=root.stat();owner=(st.st_uid,st.st_gid)
 for filename,rel in [('apx-flatpak-nesting-v1','usr/local/libexec/apx-flatpak-nesting-v1'),('apx-flatpak-nesting-v1.service','etc/systemd/system/apx-flatpak-nesting-v1.service')]:
  p=root/rel;content=(REPO/'config/environment-flatpak-v1'/filename).read_bytes()
  if not p.exists() or p.read_bytes()!=content:write(p,content,owner,0o644 if filename.endswith('.service') else 0o755)
 p=root/'etc/systemd/system/multi-user.target.wants/apx-flatpak-nesting-v1.service'
 if p.is_symlink():assert os.readlink(p)=='../apx-flatpak-nesting-v1.service'
 else:
  assert not p.exists()
  manifest.append(dict(target=str(p),existed=False,after_symlink='../apx-flatpak-nesting-v1.service',uid=owner[0],gid=owner[1],mode=0o777))
  (backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
  p.symlink_to('../apx-flatpak-nesting-v1.service');os.lchown(p,*owner)
for rel in assets:write(SEED/rel,(source/rel).read_bytes(),mode=0o755)
for p in (REPO/'config/environment-flatpak-v1').iterdir():write(Path('/usr/share/apx/config-seeds/environment-flatpak-v1')/p.name,p.read_bytes())
write(Path('/usr/lib/apx/apx_environment_desktop_defaults.py'),(REPO/'src/apx_environment_desktop_defaults.py').read_bytes())
for p in [REPO/'scripts/virtual-lab/apx-lab-runtime.py',Path('/usr/lib/apx/apx-lab-runtime.py')]:
 text=p.read_text();start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2;s=text[start:end]
 for rel in assets:
  d=hashlib.sha256((source/rel).read_bytes()).hexdigest();pat=r'("'+re.escape(rel)+r'": ")[a-f0-9]+'
  if re.search(pat,s):s=re.sub(pat,lambda m:m[1]+d,s)
  else:s=s.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    "'+rel+'": "'+d+'",')
 text=text[:start]+s+text[end:]
 if 'from apx_environment_desktop_defaults import' not in text:
  line='    from apx_environment_features import local_packages_for, packages_for, validate_selection'
  text=text.replace(line,line+'\n    from apx_environment_desktop_defaults import install_flatpak_defaults')
  marker='        if role == "graphical-base":\n            configure_environment_features(root, plan)'
  assert marker in text
  text=text.replace(marker,'        if role in GRAPHICAL_ROLES | {"hub"}:\n            install_flatpak_defaults(root)\n'+marker,1)
 write(p,text.encode())
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2));print(backup)
