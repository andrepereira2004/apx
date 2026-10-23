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
backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-environment-hardware')
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
rels=['local/bin/apx-laptop-action-v1','local/bin/apx-legion-brightness-keys-v1.py','local/libexec/apx-system-power-client-v1.py','local/libexec/apx_system_power_contract.py']
for name in names:
 home=BASE/name/'home/apx';st=home.stat();owner=(st.st_uid,st.st_gid)
 for rel in rels:
  write(home/('.'+rel),(source/rel).read_bytes(),owner,0o755)
 p=home/'.config/quickshell/apx/shell.qml';s=p.read_text()
 s=s.replace('/usr/lib/apx/apx-legion-brightness-keys-v1.py','/home/apx/.local/bin/apx-legion-brightness-keys-v1.py')
 s=s.replace('if (root.isHub) loadHardwareProfile()','loadHardwareProfile()').replace('if (root.isHub && !hardwareProfileProcess.running)','if (!hardwareProfileProcess.running)')
 s=s.replace('visible: root.isHub && root.controlsAllClosed() && root.hardwareControlError.length > 0','visible: root.controlsAllClosed() && root.hardwareControlError.length > 0').replace('visible: root.isHub && root.hardwareStatusError.length > 0','visible: root.hardwareStatusError.length > 0')
 s=s.replace('visible: root.isHub\n                        text: "Modo de energia"','visible: true\n                        text: "Modo de energia"').replace('id: energyModeRow\n                        visible: root.isHub','id: energyModeRow\n                        visible: true')
 write(p,s.encode(),owner)
 p=home/'.config/hypr/hyprland.lua';s=p.read_text()
 for line in (source/'hypr/hyprland.lua').read_text().splitlines():
  if 'Tab"' in line and 'overview' in line and line not in s:s+='\n'+line+'\n'
 write(p,s.encode(),owner)
for rel in rels+['quickshell/apx/shell.qml']:
 write(SEED/rel,(source/rel).read_bytes(),mode=0o755 if rel.startswith('local/') else 0o644)
for rel,target in [('src/apx_active_shell_peer.py','/usr/lib/apx/apx_active_shell_peer.py'),('scripts/physical-pilot/apx-environment-hardware-v1.py','/usr/lib/apx/apx-environment-hardware-v1.py'),('scripts/physical-pilot/apx-graphical-environment-v1.py','/usr/lib/apx/apx-graphical-environment-v1.py'),('config/systemd/apx-environment-hardware-v1.service','/etc/systemd/system/apx-environment-hardware-v1.service')]:
 write(Path(target),(REPO/rel).read_bytes(),mode=0o755 if '/physical-pilot/' in rel else 0o644)
for p in [REPO/'scripts/virtual-lab/apx-lab-runtime.py',Path('/usr/lib/apx/apx-lab-runtime.py')]:
 text=p.read_text();start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2
 import ast
 assets=ast.literal_eval(text[start:end].split(' = ',1)[1])
 for rel in rels+['quickshell/apx/shell.qml']:assets[rel]=hashlib.sha256((source/rel).read_bytes()).hexdigest()
 block='ENVIRONMENT_SHELL_ASSETS = '+json.dumps(assets,indent=4,sort_keys=True)
 text=(text[:start]+block+text[end:]).replace('relative.startswith("local/bin/")','relative.startswith(("local/bin/", "local/libexec/"))')
 write(p,text.encode())
p=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
s=re.sub(r'(?m)^readonly RUNTIME_SHA256=.*$', 'readonly RUNTIME_SHA256='+hashlib.sha256((REPO/'scripts/virtual-lab/apx-lab-runtime.py').read_bytes()).hexdigest(),p.read_text());write(p,s.encode())
p=Path('/etc/systemd/system/multi-user.target.wants/apx-environment-hardware-v1.service');assert not p.exists();manifest.append(dict(target=str(p),existed=False,after_symlink='../apx-environment-hardware-v1.service'));p.symlink_to('../apx-environment-hardware-v1.service')
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2));print(backup)
