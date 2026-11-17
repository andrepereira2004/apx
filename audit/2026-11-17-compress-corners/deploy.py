from pathlib import Path
import datetime,fcntl,hashlib,json,os,re,shutil,stat
repo=Path(__file__).resolve().parents[2]
assert Path('/etc/hostname').read_text().strip()=='apx-host'
relative='local/share/apx/compress.css'
source=repo/'config/environment-shell-v1'/relative
payload=source.read_bytes();digest=lambda data:hashlib.sha256(data).hexdigest()
planned={Path('/usr/share/apx/config-seeds/environment-shell-v1')/relative:payload}
for environment in Path('/var/lib/apx/environments').iterdir():
 if (environment/'registration.json').is_file():
  target=environment/'home/apx/.local/share/apx/compress.css'
  assert target.is_file();planned[target]=payload
for runtime in (repo/'scripts/virtual-lab/apx-lab-runtime.py',Path('/usr/lib/apx/apx-lab-runtime.py')):
 text,count=re.subn(r'("local/share/apx/compress\.css": ")[a-f0-9]{64}(",)',lambda m:m[1]+digest(payload)+m[2],runtime.read_text());assert count==1
 planned[runtime]=text.encode()
recovery=repo/'scripts/physical-pilot/recover-development-quota-v1.sh'
text,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+digest(planned[repo/'scripts/virtual-lab/apx-lab-runtime.py']),recovery.read_text());assert count==1
planned[recovery]=text.encode()
planned={p:data for p,data in planned.items() if p.read_bytes()!=data}
with open('/run/apx/machine-transition-v1.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-compress-corners');backup.mkdir(mode=0o700)
 entries=[]
 for target,data in planned.items():
  assert target.is_file() and not target.is_symlink();meta=target.stat()
  saved=backup/target.relative_to('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
  entries.append({'path':str(target),'before':digest(target.read_bytes()),'after':digest(data),'mode':stat.S_IMODE(meta.st_mode),'uid':meta.st_uid,'gid':meta.st_gid})
 (backup/'inventory.json').write_text(json.dumps(entries,indent=2)+'\n')
 for entry in entries:
  target=Path(entry['path']);temp=target.with_name(target.name+'.corners-new');temp.write_bytes(planned[target]);os.chmod(temp,entry['mode']);os.chown(temp,entry['uid'],entry['gid']);os.replace(temp,target)
  assert digest(target.read_bytes())==entry['after']
 print(backup);print('Verified',len(entries),'files')
