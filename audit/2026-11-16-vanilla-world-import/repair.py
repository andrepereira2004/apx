from pathlib import Path
import datetime,hashlib,json,os,subprocess,uuid
home=Path.home()
users=home/'.local/share/bedrock-on-linux/compatdata/pfx/drive_c/users/steamuser/AppData/Roaming/Minecraft Bedrock/Users'
roots=list(users.glob('*/games/com.mojang/minecraftWorlds'))
candidates=[root/'Vanilla - BEJA' for root in roots if (root/'Vanilla - BEJA/Vanilla - BEJA/level.dat').is_file()]
assert len(candidates)==1,candidates
outer=candidates[0];inner=outer/'Vanilla - BEJA'
assert sorted(p.name for p in outer.iterdir())==['Vanilla - BEJA']
assert (inner/'level.dat').is_file() and (inner/'db').is_dir()
# Refuse a live world. Wine keeps its LevelDB files open while playing.
for process in Path('/proc').iterdir():
 if not process.name.isdigit():continue
 try:
  for fd in (process/'fd').iterdir():
   try:target=os.readlink(fd)
   except OSError:continue
   if str(inner) in target:raise RuntimeError('O mundo está aberto. Fecha-o antes de reparar a pasta.')
 except (PermissionError,FileNotFoundError):pass
backup=home/'.local/state/apx-world-import-repair'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup.mkdir(parents=True,mode=0o700)
# Same Environment/Btrfs: preserve the complete imported data with reflinks.
subprocess.run(['/usr/bin/cp','-a','--reflink=always','--',str(outer),str(backup/'imported-wrapper')],check=True)
files=[p for p in inner.rglob('*') if p.is_file()]
manifest={str(p.relative_to(inner)):{'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
copy=backup/'imported-wrapper/Vanilla - BEJA'
for name,entry in manifest.items():
 p=copy/name;assert p.stat().st_size==entry['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'],name
staging=outer.with_name('.apx-world-wrapper-'+uuid.uuid4().hex)
os.rename(outer,staging)
try:
 os.rename(staging/'Vanilla - BEJA',outer)
except BaseException:
 if not outer.exists():os.rename(staging,outer)
 raise
staging.rmdir()
for name,entry in manifest.items():
 p=outer/name;assert p.stat().st_size==entry['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'],name
(backup/'repair.json').write_text(json.dumps({'world':str(outer),'backup':str(backup/'imported-wrapper'),'files':manifest},indent=2,ensure_ascii=False)+'\n')
print('PASS: world is at minecraftWorlds/Vanilla - BEJA/level.dat with db at the same root',flush=True)
print('Verified',len(manifest),'files unchanged by SHA-256 before/backup/after',flush=True)
print('BACKUP:',backup,flush=True)
