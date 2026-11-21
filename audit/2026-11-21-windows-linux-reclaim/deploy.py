#!/usr/bin/env python3
"""Install reviewed reclaim flow, without disk, encryption or boot changes."""
import ast,datetime,fcntl,hashlib,importlib.util,json,os
from pathlib import Path
import re,shutil,subprocess,tempfile,time
REPO=Path(__file__).resolve().parents[2]
NATIVE=Path('/var/lib/apx/native-environments')
MANIFEST=Path('/usr/share/apx/native-v3-enabled.json')
GEN='2770478b-480f-4aea-8910-e3201d5334c5'
def sha(data):return hashlib.sha256(data).hexdigest()
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run(*args):return subprocess.check_output(args,stderr=subprocess.STDOUT)
def atomic(path,data,mode,uid=0,gid=0):
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix='.apx-reclaim-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:
   os.fchmod(f.fileno(),mode);os.fchown(f.fileno(),uid,gid);f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:Path(tmp).unlink(missing_ok=True)
def main():
 assert Path('/etc/hostname').read_text().strip()=='apx-host'
 assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
 assert Path('/sys/class/block/nvme0n1/device/serial').read_text().strip()=='S4DYNX0R253702'
 assert not (NATIVE/'pending-v3.json').exists()
 assert not Path('/run/apx/environment-management-v1.lock').exists()
 before_gpt=run('sfdisk','--dump','/dev/nvme0n1');before_firmware=run('efibootmgr','-v')
 before_boot={str(p):sha(p.read_bytes()) for p in Path('/boot/EFI/APX').glob('*.efi')}
 release=json.loads(MANIFEST.read_bytes())
 for name,expected in release['files'].items():assert sha(Path(name).read_bytes())==expected,name
 candidate=load(REPO/'src/apx_native_hub_v3.py','candidate_release')
 planned={}
 sources={
  '/usr/lib/apx/apx-native-lifecycle-v3.py':'scripts/physical-pilot/apx-native-lifecycle-v3.py',
  '/usr/lib/apx/apx-environment-switch-v1.py':'scripts/physical-pilot/apx-environment-switch-v1.py',
  '/usr/lib/apx/apx_native_hub_v3.py':'src/apx_native_hub_v3.py',
  '/usr/lib/apx/apx_native_linux_reclaim_v3.py':'src/apx_native_linux_reclaim_v3.py',
  '/usr/lib/apx/apx-reclaim-windows-linux-v3.py':'scripts/physical-pilot/apx-reclaim-windows-linux-v3.py',
  '/usr/local/sbin/apx-concluir-remocao-windows':'scripts/physical-pilot/apx-concluir-remocao-windows'}
 for dest,src in sources.items():planned[Path(dest)]=(REPO/src).read_bytes()
 source=(REPO/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
 old_confirm='Apaga só este Windows e o seu EFI. Os 80 GiB ficam reservados para outro Windows; não é apagamento seguro.'
 new_confirm='Remove este Windows e integra o espaço no Linux. Requer a palavra-passe de cifragem num terminal local; os outros Windows são preservados.'
 status='text: root.environmentManagementState.pending_stage === "deleting" ? '
 new_status='text: root.environmentManagementState.native_v3_local_auth === true ? "Windows removido. Falta confirmar a cifragem num terminal local do Host para integrar o espaço no Linux. A operação ainda não terminou." : root.environmentManagementState.pending_stage === "deleting" ? '
 start=source.index('                        Text { renderType: Text.QtRendering; visible: root.environmentManagementState.native_v3_local_auth === true')
 needle='                        MenuButton { visible: root.environmentManagementState.native_v3_activate === true; width: parent.width; height: visible ? Appearance.menuActionHeight : 0'
 extra=source[start:source.index(needle,start)]
 bases=[Path('/usr/share/apx/config-seeds/environment-shell-v1')]+[Path('/var/lib/apx/environments')/n/'home/apx/.config' for n in ('hub','faculdade','hytale','minecraft','steam')]
 for base in bases:
  path=base/'quickshell/apx/shell.qml';text=path.read_text()
  for old,new in ((old_confirm,new_confirm),(status,new_status),(needle,extra+needle)):
   assert text.count(old)==1,(path,old[:50]);text=text.replace(old,new)
  planned[path]=text.encode()
 for runtime,base in ((REPO/'scripts/virtual-lab/apx-lab-runtime.py',REPO/'config/environment-shell-v1'),(Path('/usr/lib/apx/apx-lab-runtime.py'),bases[0])):
  text=runtime.read_text();start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2
  section=text[start:end];digest=sha((base/'quickshell/apx/shell.qml').read_bytes() if base==REPO/'config/environment-shell-v1' else planned[base/'quickshell/apx/shell.qml'])
  section,count=re.subn(r'("quickshell/apx/shell.qml": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest+m[2],section);assert count==1
  planned[runtime]=(text[:start]+section+text[end:]).encode()
 recovery=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
 text,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+sha(planned[REPO/'scripts/virtual-lab/apx-lab-runtime.py']),recovery.read_text());assert count==1
 planned[recovery]=text.encode()
 updated=dict(release,files={name:sha(planned.get(Path(name),Path(name).read_bytes() if Path(name).exists() else b'')) for name in candidate.CRITICAL})
 assert set(updated['files'])-set(release['files'])=={'/usr/lib/apx/apx_native_linux_reclaim_v3.py','/usr/lib/apx/apx-reclaim-windows-linux-v3.py','/usr/local/sbin/apx-concluir-remocao-windows'}
 planned[MANIFEST]=(json.dumps(updated,sort_keys=True)+'\n').encode()
 # Queue the already-cleared Faculty slot as an unfinished reclaim, never as success.
 marker=json.loads((NATIVE/'free-slot-v3.json').read_bytes());assert marker['previous_generation']==GEN
 pending=dict(schema=3,profile='apx-native-job-v3',generation=GEN,target='windows-testes',
              stage='awaiting-linux-auth',mode='linux-reclaim',action='native-delete-v3')
 planned[NATIVE/'pending-v3.json']=json.dumps(pending,sort_keys=True).encode()
 state=Path('/run/apx/environment-management-v1.json')
 planned[state]=json.dumps(dict(schema=1,profile='apx-environment-management-v1',action='native-delete-v3',
   target='windows-testes',phase='awaiting-local-auth',progress=75,message='Windows Faculdade removido; falta confirmar localmente a cifragem para integrar o espaço no Linux.',updated_at=int(time.time()))).encode()
 backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-windows-linux-reclaim');backup.mkdir(mode=0o700)
 inventory=[]
 for path,data in planned.items():
  st=path.stat() if path.exists() else None
  if st:
   dest=backup/str(path).lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
  mode=st.st_mode&0o777 if st else (0o755 if str(path) in sources and (path.name.endswith('.py') or path.name=='apx-concluir-remocao-windows') else 0o400)
  if path.name=='apx_native_linux_reclaim_v3.py':mode=0o644
  inventory.append(dict(path=str(path),existed=bool(st),mode=mode,uid=st.st_uid if st else 0,gid=st.st_gid if st else 0,before=sha(path.read_bytes()) if st else None,after=sha(data)))
 (backup/'inventory.json').write_text(json.dumps(inventory,indent=2))
 try:
  for item in inventory:
   path=Path(item['path']);atomic(path,planned[path],item['mode'],item['uid'],item['gid'])
  assert run('sfdisk','--dump','/dev/nvme0n1')==before_gpt
  assert run('efibootmgr','-v')==before_firmware
  assert {str(p):sha(p.read_bytes()) for p in Path('/boot/EFI/APX').glob('*.efi')}==before_boot
  run('python3',str(REPO/'scripts/physical-pilot/check-native-release-v3.py'))
  endpoint=Path('/run/apx/environment-switch-v1.sock');old_inode=endpoint.stat().st_ino
  run('systemctl','restart','apx-environment-switch-v1.service')
  for _ in range(50):
   if endpoint.exists() and endpoint.stat().st_ino!=old_inode:break
   time.sleep(.1)
  else:raise RuntimeError('socket unavailable')
  active=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_bytes())
  fields=Path('/proc/'+str(active['pid'])+'/uid_map').read_text().split();assert len(fields)==3 and fields[0]=='0' and fields[2]=='65536'
  os.chown(endpoint,int(fields[1])+1000,int(fields[1])+1000);os.chmod(endpoint,0o660)
  load(REPO/'scripts/physical-pilot/deploy-environment-icons-20261020.py','refresh').refresh_socket(int(active['pid']))
  assert run('systemctl','is-active','apx-environment-switch-v1.service').strip()==b'active'
 except BaseException:
  for item in reversed(inventory):
   path=Path(item['path'])
   if item['existed']:atomic(path,(backup/str(path).lstrip('/')).read_bytes(),item['mode'],item['uid'],item['gid'])
   else:path.unlink(missing_ok=True)
  raise
 print(json.dumps({'backup':str(backup),'files':len(inventory),'physical_disk_changed':False,'boot_changed':False,'status':'awaiting-local-auth'}))
if __name__=='__main__':
 with open('/run/apx/machine-transition-v1.lock','a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);main()
