from pathlib import Path
import datetime, fcntl, hashlib, json, os, re, shutil, stat
import xml.etree.ElementTree as ET
repo = Path(__file__).resolve().parents[2]
assert Path('/etc/hostname').read_text().strip() == 'apx-host'
assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text()
source = repo/'config/environment-shell-v1'
assets = {name: source/name for name in ('local/lib/apx/chooser-places.c','local/lib/apx/wallpaper-used.h','local/lib/apx/libchooser-places.so','local/libexec/apx-thunar-chrome-v1.so','local/bin/apx-share-copy-v1','quickshell/apx/PersonalizationPanel.qml','Thunar/uca.xml')}
homes = [p/'home/apx' for p in Path('/var/lib/apx/environments').iterdir() if (p/'registration.json').is_file()]
planned={}
for relative, origin in assets.items():
 planned[Path('/usr/share/apx/config-seeds/environment-shell-v1')/relative] = origin.read_bytes()
 for home in homes:
  target = home/('.local' if relative.startswith('local/') else '.config')/(relative.removeprefix('local/') if relative.startswith('local/') else relative)
  if relative == 'Thunar/uca.xml':
   if not target.exists(): continue
   tree=ET.fromstring(target.read_bytes())
   if any(x.findtext('unique-id')=='1795270000000000-1' for x in tree): continue
   tree.append(ET.fromstring(origin.read_bytes())[-1]); planned[target]=ET.tostring(tree,encoding='utf-8')+b'\n'
  else: planned[target]=origin.read_bytes()
digest=lambda data:hashlib.sha256(data).hexdigest()
for runtime in (repo/'scripts/virtual-lab/apx-lab-runtime.py',Path('/usr/lib/apx/apx-lab-runtime.py')):
 text=runtime.read_text()
 for relative,origin in assets.items():
  pattern=r'("'+re.escape(relative)+r'": ")[a-f0-9]{64}("[,])'
  text,count=re.subn(pattern,lambda m:m[1]+digest(origin.read_bytes())+m[2],text)
  assert count in (0,1)
  if not count: text=text.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    "'+relative+'": "'+digest(origin.read_bytes())+'",',1)
 planned[runtime]=text.encode()
p=repo/'scripts/physical-pilot/recover-development-quota-v1.sh'
text,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+digest(planned[repo/'scripts/virtual-lab/apx-lab-runtime.py']),p.read_text());assert count==1
planned[p]=text.encode()
planned[Path('/usr/lib/apx/apx-transfer-v1.py')]=(repo/'scripts/physical-pilot/apx-transfer-v1.py').read_bytes()
planned={p:data for p,data in planned.items() if not p.exists() or p.read_bytes()!=data}
with open('/run/apx/machine-transition-v1.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-wallpaper-sharing');backup.mkdir(mode=0o700)
 inventory=[]
 for target,data in planned.items():
  assert not target.is_symlink()
  meta=target.stat() if target.exists() else target.parent.stat()
  mode=stat.S_IMODE(meta.st_mode) if target.exists() else 0o644
  entry=dict(path=str(target),before=digest(target.read_bytes()) if target.exists() else None,after=digest(data),uid=meta.st_uid,gid=meta.st_gid,mode=mode)
  if target.exists():
   saved=backup/target.relative_to('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
  inventory.append(entry)
 (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
 for entry in inventory:
  target=Path(entry['path']);temporary=target.with_name(target.name+'.wallpaper-new');temporary.write_bytes(planned[target]);os.chmod(temporary,entry['mode']);os.chown(temporary,entry['uid'],entry['gid']);os.replace(temporary,target)
  assert digest(target.read_bytes())==entry['after']
 print(backup);print('Verified',len(inventory),'files,',len(homes),'homes')
