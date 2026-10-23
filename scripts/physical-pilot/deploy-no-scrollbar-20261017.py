#!/usr/bin/env python3
"""Reversible fixed-pilot volume and brightness OSD geometry correction."""
from pathlib import Path
import datetime,fcntl,hashlib,importlib.util,json,os,re,shutil,sys,time
REPO=Path(__file__).resolve().parents[2]
AUDIT=REPO/'audit/2026-10-17-no-scrollbar'
SOURCE=REPO/'config/environment-shell-v1'
SEED=Path('/usr/share/apx/config-seeds/environment-shell-v1')
spec=importlib.util.spec_from_file_location('no_scrollbar_transform',AUDIT/'transform.py');transform=importlib.util.module_from_spec(spec);spec.loader.exec_module(transform)
def atomic(path,data,mode,uid,gid):
 assert not path.is_symlink(),path
 temp=path.with_name(path.name+'.control-centre-tmp');temp.write_bytes(data);os.chmod(temp,mode);os.chown(temp,uid,gid);os.replace(temp,path)
def main():
 assert Path('/etc/hostname').read_text().strip()=='apx-host'
 assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
 assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
 homes=[Path('/var/lib/apx/environments')/n/'home/apx' for n in ['hub','faculdade','hytale','minecraft','steam']]
 if len(sys.argv)==3 and sys.argv[1]=='--rollback':
  backup=Path(sys.argv[2]).resolve();assert backup.parent==Path('/var/lib/apx/backups') and backup.name.endswith('-no-scrollbar')
  for item in json.loads((backup/'inventory.json').read_text()):
   if item.get('existed',True):atomic(Path(item['path']),(backup/item['path'].lstrip('/')).read_bytes(),item['mode'],item['uid'],item['gid'])
   elif Path(item['path']).exists():Path(item['path']).unlink()
  for home in homes:(home/'.config/quickshell/apx/shell.qml').touch()
  print('Restored',backup);return
 assert sys.argv[1:] in ([],['--check'])
 planned={}
 for base in [SOURCE,SEED]+homes:
  for rel in transform.RELATIVES:
   path=base/rel if base in [SOURCE,SEED] else base/'.config'/rel
   assert not path.is_symlink(),path
   assert path.is_file() or rel.endswith('.svg'),path
   planned[path]=transform.transform(rel,path.read_text() if path.exists() else '').encode()
 for runtime,base in [(REPO/'scripts/virtual-lab/apx-lab-runtime.py',SOURCE),(Path('/usr/lib/apx/apx-lab-runtime.py'),SEED)]:
  text=runtime.read_text();start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2;section=text[start:end]
  for rel in transform.RELATIVES:
   digest=hashlib.sha256(planned[base/rel]).hexdigest()
   section,n=re.subn(r'("'+re.escape(rel)+r'": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest+m[2],section);assert n<=1,rel
   if not n:section=section.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    '+json.dumps(rel)+': '+json.dumps(digest)+',',1)
  planned[runtime]=(text[:start]+section+text[end:]).encode()
 recovery=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
 text,n=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+hashlib.sha256(planned[REPO/'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(),recovery.read_text());assert n==1
 planned[recovery]=text.encode();planned={p:d for p,d in planned.items() if not p.exists() or p.read_bytes()!=d}
 if sys.argv[1:]==['--check']:
  (AUDIT/'planned-paths.json').write_text(json.dumps([str(p) for p in planned],indent=2)+'\n')
  for rel in transform.RELATIVES:
   dest=AUDIT/'candidate'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(transform.transform(rel,(SOURCE/rel).read_text() if (SOURCE/rel).exists() else ''))
  print('Planned',len(planned),'files');return
 if not planned:print('OSD geometry already updated.');return
 backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-no-scrollbar');backup.mkdir(parents=True)
 inventory=[]
 for path,data in planned.items():
  existed=path.exists();stat=path.stat() if existed else path.parent.stat();saved=backup/str(path).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True)
  if existed:shutil.copy2(path,saved)
  inventory.append(dict(path=str(path),existed=existed,mode=stat.st_mode&0o777 if existed else 0o644,uid=stat.st_uid,gid=stat.st_gid,before=hashlib.sha256(path.read_bytes()).hexdigest() if existed else None,after=hashlib.sha256(data).hexdigest()))
 (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
 for item in sorted(inventory,key=lambda i:Path(i['path']).name=='shell.qml'):
  path=Path(item['path']);atomic(path,planned[path],item['mode'],item['uid'],item['gid']);assert path.read_bytes()==planned[path]
 # A dependency reload may already be compiling while assets are being replaced.
 # Retouch the entry point after that reload, so it cannot keep cached old root code.
 time.sleep(2)
 for home in homes:(home/'.config/quickshell/apx/shell.qml').touch()
 pointer=AUDIT/'baseline-backup.txt'
 if not pointer.exists():pointer.write_text(str(backup)+'\n')
 print(backup);print('Verified',len(planned),'files')
if __name__=='__main__':
 with open('/run/apx/machine-transition-v1.lock','a') as lock:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);main()
