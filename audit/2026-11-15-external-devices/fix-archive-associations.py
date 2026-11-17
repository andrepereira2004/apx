from pathlib import Path
import datetime,fcntl,hashlib,json,os,re,shutil
repo=Path(__file__).resolve().parents[2]
formats=('application/zip','application/x-zip','application/x-zip-compressed','application/x-7z-compressed','application/vnd.rar','application/x-rar','application/x-rar-compressed','application/x-tar','application/x-compressed-tar','application/gzip','application/x-gzip','application/x-bzip','application/x-bzip-compressed-tar','application/x-xz','application/x-xz-compressed-tar','application/zstd','application/x-zstd-compressed-tar')
def update(text):
 lines=text.splitlines();section=None;found=set()
 for i,line in enumerate(lines):
  if line.startswith('['):section=line
  elif section=='[Added Associations]' and '=' in line:
   key,values=line.split('=',1)
   if key in formats:
    apps=[a for a in values.split(';') if a]
    if 'org.gnome.FileRoller.desktop' not in apps:apps.append('org.gnome.FileRoller.desktop')
    lines[i]=key+'='+';'.join(apps)+';';found.add(key)
 additions=[mime+'=org.gnome.FileRoller.desktop;' for mime in formats if mime not in found]
 if '[Added Associations]' not in lines:lines+=['','[Added Associations]']
 start=lines.index('[Added Associations]')+1
 lines[start:start]=additions
 return '\n'.join(lines)+'\n'
assert Path('/etc/hostname').read_text().strip()=='apx-host'
assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text()
with open('/run/apx/machine-transition-v1.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 source=repo/'config/environment-shell-v1/mimeapps.list'
 planned={source:update(source.read_text()).encode()}
 planned[Path('/usr/share/apx/config-seeds/environment-shell-v1/mimeapps.list')]=planned[source]
 for name in ('faculdade','hytale','minecraft','steam'):
  p=Path('/var/lib/apx/environments')/name/'home/apx/.config/mimeapps.list'
  planned[p]=update(p.read_text()).encode()
 digest=lambda data:hashlib.sha256(data).hexdigest()
 for p in (repo/'scripts/virtual-lab/apx-lab-runtime.py',Path('/usr/lib/apx/apx-lab-runtime.py')):
  data,n=re.subn(r'("mimeapps.list": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest(planned[source])+m[2],p.read_text());assert n==1;planned[p]=data.encode()
 p=repo/'scripts/physical-pilot/recover-development-quota-v1.sh'
 data,n=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+digest(planned[repo/'scripts/virtual-lab/apx-lab-runtime.py']),p.read_text());assert n==1;planned[p]=data.encode()
 planned={p:d for p,d in planned.items() if p.read_bytes()!=d}
 backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-archive-associations');backup.mkdir()
 inventory=[]
 for p,data in planned.items():
  assert p.is_file() and not p.is_symlink();s=p.stat();saved=backup/p.relative_to('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,saved)
  inventory.append({'path':str(p),'before':digest(p.read_bytes()),'after':digest(data),'mode':s.st_mode&0o777,'uid':s.st_uid,'gid':s.st_gid})
 (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
 for p,data in planned.items():
  s=p.stat();tmp=p.with_name(p.name+'.apx-archive-tmp');tmp.write_bytes(data);os.chmod(tmp,s.st_mode&0o777);os.chown(tmp,s.st_uid,s.st_gid);os.replace(tmp,p);assert p.read_bytes()==data
 print(backup);print('Verified',len(planned),'files')
