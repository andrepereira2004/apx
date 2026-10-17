#!/usr/bin/env python3
"""Reversible, fixed-pilot typography, grouping and staged submenu correction."""
from pathlib import Path
import datetime,fcntl,hashlib,importlib.util,json,os,re,shutil,sys
REPO=Path(__file__).resolve().parents[2]
AUDIT=REPO/'audit/2026-10-17-shell-consistency'
SOURCE=REPO/'config/environment-shell-v1'
SEED=Path('/usr/share/apx/config-seeds/environment-shell-v1')
spec=importlib.util.spec_from_file_location('consistency_transform',AUDIT/'transform.py');transform=importlib.util.module_from_spec(spec);spec.loader.exec_module(transform)
def atomic(path,data,mode,uid,gid):
 assert not path.is_symlink(),path
 temp=path.with_name(path.name+'.consistency-tmp');temp.write_bytes(data);os.chmod(temp,mode);os.chown(temp,uid,gid);os.replace(temp,path)
def main():
 assert Path('/etc/hostname').read_text().strip()=='apx-host'
 assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
 assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
 homes=[Path('/var/lib/apx/environments')/n/'home/apx' for n in ['hub','faculdade','hytale','minecraft','steam']]
 if len(sys.argv)==3 and sys.argv[1]=='--rollback':
  backup=Path(sys.argv[2]).resolve();assert backup.parent==Path('/var/lib/apx/backups') and backup.name.endswith('-shell-consistency')
  for item in json.loads((backup/'inventory.json').read_text()):atomic(Path(item['path']),(backup/item['path'].lstrip('/')).read_bytes(),item['mode'],item['uid'],item['gid'])
  for home in homes:(home/'.config/quickshell/apx/shell.qml').touch()
  print('Restored',backup);return
 assert sys.argv[1:] in ([],['--check'])
 planned={}
 for base in [SOURCE,SEED]+homes:
  for rel in transform.RELATIVES:
   path=base/rel if base in [SOURCE,SEED] else base/'.config'/rel
   assert path.is_file() and not path.is_symlink(),path
   planned[path]=transform.transform(rel,path.read_text()).encode()
 for runtime,base in [(REPO/'scripts/virtual-lab/apx-lab-runtime.py',SOURCE),(Path('/usr/lib/apx/apx-lab-runtime.py'),SEED)]:
  text=runtime.read_text();start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2;section=text[start:end]
  for rel in transform.RELATIVES:
   digest=hashlib.sha256(planned[base/rel]).hexdigest()
   section,n=re.subn(r'("'+re.escape(rel)+r'": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest+m[2],section);assert n==1,rel
  planned[runtime]=(text[:start]+section+text[end:]).encode()
 recovery=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
 text,n=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+hashlib.sha256(planned[REPO/'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(),recovery.read_text());assert n==1
 planned[recovery]=text.encode();planned={p:d for p,d in planned.items() if p.read_bytes()!=d}
 if sys.argv[1:]==['--check']:
  (AUDIT/'planned-paths.json').write_text(json.dumps([str(p) for p in planned],indent=2)+'\n')
  for rel in transform.RELATIVES:
   dest=AUDIT/'candidate'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(transform.transform(rel,(SOURCE/rel).read_text()))
  print('Planned',len(planned),'files');return
 if not planned:print('Shell consistency already installed.');return
 backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-shell-consistency');backup.mkdir(parents=True)
 inventory=[]
 for path,data in planned.items():
  stat=path.stat();saved=backup/str(path).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,saved)
  inventory.append(dict(path=str(path),mode=stat.st_mode&0o777,uid=stat.st_uid,gid=stat.st_gid,before=hashlib.sha256(path.read_bytes()).hexdigest(),after=hashlib.sha256(data).hexdigest()))
 (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
 for item in sorted(inventory,key=lambda i:Path(i['path']).name=='shell.qml'):
  path=Path(item['path']);atomic(path,planned[path],item['mode'],item['uid'],item['gid']);assert path.read_bytes()==planned[path]
 for home in homes:(home/'.config/quickshell/apx/shell.qml').touch()
 pointer=AUDIT/'baseline-backup.txt'
 if not pointer.exists():pointer.write_text(str(backup)+'\n')
 print(backup);print('Verified',len(planned),'files')
if __name__=='__main__':
 with open('/run/apx/machine-transition-v1.lock','a') as lock:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);main()
