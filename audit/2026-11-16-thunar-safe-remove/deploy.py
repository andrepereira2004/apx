from pathlib import Path
import datetime,fcntl,hashlib,json,os,re,shutil,stat
repo=Path(__file__).resolve().parents[2]
assert Path('/etc/hostname').read_text().strip()=='apx-host'
assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text()
source=repo/'config/environment-shell-v1'
assets={relative:source/relative for relative in (
 'local/lib/apx/chooser-places.c','local/lib/apx/libchooser-places.so',
 'local/bin/apx-removable-action-v1','local/bin/apx-removable-notifications-v1','local/bin/apx-shell-v1')}
base=Path('/var/lib/apx/environments')
homes=[p/'home/apx' for p in sorted(base.iterdir()) if (p/'registration.json').is_file()]
assert len(homes)==5
planned={}
for relative,origin in assets.items():
 planned[Path('/usr/share/apx/config-seeds/environment-shell-v1')/relative]=origin.read_bytes()
 for home in homes:
  target=home/'.local'/relative.removeprefix('local/')
  planned[target]=origin.read_bytes()
digest=lambda data:hashlib.sha256(data).hexdigest()
for runtime in (repo/'scripts/virtual-lab/apx-lab-runtime.py',Path('/usr/lib/apx/apx-lab-runtime.py')):
 content=runtime.read_text()
 for relative,origin in assets.items():
  pattern=r'("'+re.escape(relative)+r'": ")[a-f0-9]{64}("[,])'
  content,count=re.subn(pattern,lambda m:m[1]+digest(origin.read_bytes())+m[2],content)
  assert count in (0,1)
  if not count: content=content.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    "'+relative+'": "'+digest(origin.read_bytes())+'",',1)
 planned[runtime]=content.encode()
recovery=repo/'scripts/physical-pilot/recover-development-quota-v1.sh'
content,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+digest(planned[repo/'scripts/virtual-lab/apx-lab-runtime.py']),recovery.read_text());assert count==1
planned[recovery]=content.encode()
host_sources={
 Path('/usr/lib/apx/apx-removable-media-v1.py'):repo/'scripts/physical-pilot/apx-removable-media-v1.py',
 Path('/usr/lib/apx/apx-host-services-v3.py'):repo/'scripts/physical-pilot/apx-host-services-v3.py',
 Path('/usr/lib/apx/apx_host_services_v3_contract.py'):repo/'src/apx_host_services_v3_contract.py'}
for target,origin in host_sources.items():planned[target]=origin.read_bytes()
for name in ('faculdade','hytale','minecraft','steam'):
 planned[base/name/'root/usr/bin/thunar']=(base/'faculdade/root/var/tmp/thunar-4.20.10/thunar/.libs/thunar').read_bytes()
planned={p:data for p,data in planned.items() if not p.exists() or p.read_bytes()!=data}
with open('/run/apx/machine-transition-v1.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-thunar-safe-remove');backup.mkdir(mode=0o700)
 inventory=[]
 for target,data in planned.items():
  assert not target.is_symlink()
  meta=target.stat() if target.exists() else target.parent.stat()
  entry={'path':str(target),'before':digest(target.read_bytes()) if target.exists() else None,'after':digest(data),'uid':meta.st_uid,'gid':meta.st_gid,'mode':stat.S_IMODE(meta.st_mode) if target.exists() else (0o755 if target.parent.name=='bin' else 0o644)}
  if target.exists():
   saved=backup/target.relative_to('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
  inventory.append(entry)
 (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
 for entry in inventory:
  target=Path(entry['path']);data=planned[target]
  if target in host_sources:
   target.write_bytes(data) # Retain inodes bound into active Environments.
  else:
   temp=target.with_name(target.name+'.safe-remove-new');temp.write_bytes(data)
   os.chmod(temp,entry['mode']);os.chown(temp,entry['uid'],entry['gid']);os.replace(temp,target)
  assert digest(target.read_bytes())==entry['after']
 print(backup);print('Verified',len(inventory),'files')
