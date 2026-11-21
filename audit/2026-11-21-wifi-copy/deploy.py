from pathlib import Path
import datetime,hashlib,json,os,re,shutil,stat,fcntl
repo=Path(__file__).resolve().parents[2]
assert Path('/etc/hostname').read_text().strip()=='apx-host'
assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
source=repo/'config/environment-shell-v1/quickshell/apx/shell.qml'
seed=Path('/usr/share/apx/config-seeds/environment-shell-v1/quickshell/apx/shell.qml')
targets=[source,seed]+[p/'home/apx/.config/quickshell/apx/shell.qml' for p in Path('/var/lib/apx/environments').iterdir() if (p/'registration.json').is_file()]
planned={}
for p in targets:
 s=p.read_text()
 before='visible: root.wifiIsKnown(root.wifiSelectedSsid) || root.wifiIsOpen(root.wifiSelectedSsid)'
 after='visible: !root.wifiIsKnown(root.wifiSelectedSsid) && root.wifiIsOpen(root.wifiSelectedSsid)'
 assert s.count(before)==1;s=s.replace(before,after,1)
 before='text: root.wifiIsKnown(root.wifiSelectedSsid) ? "As credenciais guardadas serão usadas para ligar." : "Esta rede não pede palavra-passe."'
 assert s.count(before)==1;s=s.replace(before,'text: "Esta rede não pede palavra-passe."',1)
 planned[p]=s.encode()
digest=lambda data:hashlib.sha256(data).hexdigest()
for runtime,asset in ((repo/'scripts/virtual-lab/apx-lab-runtime.py',planned[source]),(Path('/usr/lib/apx/apx-lab-runtime.py'),planned[seed])):
 text,count=re.subn(r'("quickshell/apx/shell.qml": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest(asset)+m[2],runtime.read_text());assert count==1;planned[runtime]=text.encode()
p=repo/'scripts/physical-pilot/recover-development-quota-v1.sh';text,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+digest(planned[repo/'scripts/virtual-lab/apx-lab-runtime.py']),p.read_text());assert count==1;planned[p]=text.encode()
with open('/run/apx/machine-transition-v1.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-wifi-copy');backup.mkdir(mode=0o700)
 inventory=[]
 for target,data in planned.items():
  assert not target.is_symlink();meta=target.stat();saved=backup/target.relative_to('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
  inventory.append(dict(path=str(target),before=digest(target.read_bytes()),after=digest(data),uid=meta.st_uid,gid=meta.st_gid,mode=stat.S_IMODE(meta.st_mode)))
 (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
 for e in inventory:
  target=Path(e['path']);temp=target.with_name(target.name+'.wifi-new');temp.write_bytes(planned[target]);os.chmod(temp,e['mode']);os.chown(temp,e['uid'],e['gid']);os.replace(temp,target)
 print(backup)
