from pathlib import Path
import datetime,hashlib,json,fcntl,os,re,shutil,stat
repo=Path(__file__).resolve().parents[2]
assert Path('/etc/hostname').read_text().strip()=='apx-host'
assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
planned={Path('/usr/lib/apx/apx_package_freshness.py'):(repo/'src/apx_package_freshness.py').read_bytes(),Path('/usr/lib/apx/apx_environment_features.py'):(repo/'src/apx_environment_features.py').read_bytes()}
runtime=Path('/usr/lib/apx/apx-lab-runtime.py');text=runtime.read_text();needle='        artifact = validated_local_package_artifact(package)'
assert text.count(needle)==1
text=text.replace(needle,needle+'\n        from apx_package_freshness import ensure_current_package\n        try:\n            artifact = ensure_current_package(package, artifact, LOCAL_PACKAGE_ARTIFACTS)\n        except Exception as error:\n            raise Refusal("Não foi possível obter a versão atual de " + package + ": " + str(error)) from error',1);planned[runtime]=text.encode()
digest=lambda data:hashlib.sha256(data).hexdigest()
p=repo/'scripts/physical-pilot/recover-development-quota-v1.sh'
text,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+digest((repo/'scripts/virtual-lab/apx-lab-runtime.py').read_bytes()),p.read_text());assert count==1;planned[p]=text.encode()
with open('/run/apx/machine-transition-v1.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-fresh-app-installs');backup.mkdir(mode=0o700)
 inventory=[]
 for target,data in planned.items():
  assert not target.is_symlink();meta=target.stat() if target.exists() else target.parent.stat()
  if target.exists():
   saved=backup/target.relative_to('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
  inventory.append(dict(path=str(target),before=digest(target.read_bytes()) if target.exists() else None,after=digest(data),uid=meta.st_uid,gid=meta.st_gid,mode=stat.S_IMODE(meta.st_mode) if target.exists() else 0o644))
 (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
 for entry in inventory:
  target=Path(entry['path']);stage=target.with_name(target.name+'.fresh-new');stage.write_bytes(planned[target]);os.chmod(stage,entry['mode']);os.chown(stage,entry['uid'],entry['gid']);os.replace(stage,target)
  assert digest(target.read_bytes())==entry['after']
 print(backup)
