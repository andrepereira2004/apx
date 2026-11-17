from pathlib import Path
import datetime,fcntl,hashlib,json,os,re,shutil,stat
repo=Path(__file__).resolve().parents[2]
assert Path('/etc/hostname').read_text().strip()=='apx-host'
assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text()
source=repo/'config/environment-shell-v1'
relatives=(
 'local/bin/apx-battery-notifications-v1','local/bin/apx-shell-v1',
 'local/bin/apx-compress-v1','local/lib/apx/apx_compression.py','local/share/apx/compress.css',
 'Thunar/uca.xml','gtk-3.0/bookmarks','local/libexec/apx-thunar-chrome-v1.so','local/bin/apx-window-apps-v1',
 'quickshell/apx/icons/rofi/app-window.svg','quickshell/apx/icons/rofi/terminal.svg',
)
assets={relative:source/relative for relative in relatives}
base=Path('/var/lib/apx/environments')
homes=[p/'home/apx' for p in sorted(base.iterdir()) if (p/'registration.json').is_file()]
assert len(homes)==5
planned={}
action=(Path(__file__).parent/'compress-action.xml').read_text()
for relative,origin in assets.items():
 planned[Path('/usr/share/apx/config-seeds/environment-shell-v1')/relative]=origin.read_bytes()
 for home in homes:
  if relative=='gtk-3.0/bookmarks':continue  # Preserve user/dynamic USB bookmarks.
  target=(home/'.local'/relative.removeprefix('local/')) if relative.startswith('local/') else home/'.config'/relative
  if relative=='local/libexec/apx-thunar-chrome-v1.so' and not target.exists():continue
  if relative=='Thunar/uca.xml':
   text=target.read_text() if target.exists() else '<actions>\n</actions>\n'
   if 'apx-compress-v1' not in text:
    assert text.count('</actions>')==1;text=text.replace('</actions>',action+'</actions>')
   planned[target]=text.encode()
  else:planned[target]=origin.read_bytes()
digest=lambda data:hashlib.sha256(data).hexdigest()
for runtime in (repo/'scripts/virtual-lab/apx-lab-runtime.py',Path('/usr/lib/apx/apx-lab-runtime.py')):
 content=runtime.read_text()
 content=content.replace('            if relative.startswith("apx/wallpapers/")\n            else MAX_GRAPHICAL_CONFIG_BYTES\n','            if relative.startswith("apx/wallpapers/")\n            else 2 * MAX_GRAPHICAL_CONFIG_BYTES\n            if relative == "local/libexec/apx-xdph-v1"\n            else MAX_GRAPHICAL_CONFIG_BYTES\n')
 pin_origins=dict(assets)
 if runtime==repo/'scripts/virtual-lab/apx-lab-runtime.py':
  # Keep the repository's existing profile distinct from the installed seed.
  # These three previously stale references describe source files only.
  for relative in ('quickshell/apx/ControlDashboard.qml','quickshell/apx/WorkspaceStrip.qml','hypr/hyprland.lua'):
   pin_origins[relative]=source/relative
 for relative,origin in pin_origins.items():
  content,count=re.subn(r'("'+re.escape(relative)+r'": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest(origin.read_bytes())+m[2],content)
  assert count in (0,1)
  if not count:content=content.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    "'+relative+'": "'+digest(origin.read_bytes())+'",',1)
 planned[runtime]=content.encode()
recovery=repo/'scripts/physical-pilot/recover-development-quota-v1.sh'
content,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+digest(planned[repo/'scripts/virtual-lab/apx-lab-runtime.py']),recovery.read_text());assert count==1
planned[recovery]=content.encode()
planned={p:data for p,data in planned.items() if not p.exists() or p.read_bytes()!=data}
with open('/run/apx/machine-transition-v1.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-apx-compression-rofi');backup.mkdir(mode=0o700)
 inventory=[]
 for target,data in planned.items():
  assert not target.is_symlink()
  parent=target.parent
  while not parent.exists():parent=parent.parent
  meta=target.stat() if target.exists() else parent.stat()
  entry={'path':str(target),'before':digest(target.read_bytes()) if target.exists() else None,'after':digest(data),'uid':meta.st_uid,'gid':meta.st_gid,'mode':stat.S_IMODE(meta.st_mode) if target.exists() else (0o755 if target.parent.name=='bin' else 0o644)}
  if target.exists():
   saved=backup/target.relative_to('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
  inventory.append(entry)
 (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
 for entry in inventory:
  target=Path(entry['path']);data=planned[target]
  missing=[];parent=target.parent
  while not parent.exists():missing.append(parent);parent=parent.parent
  for directory in reversed(missing):
   directory.mkdir(mode=0o755);os.chown(directory,entry['uid'],entry['gid'])
  temp=target.with_name(target.name+'.apx-compress-new');temp.write_bytes(data)
  os.chmod(temp,entry['mode']);os.chown(temp,entry['uid'],entry['gid']);os.replace(temp,target)
  assert digest(target.read_bytes())==entry['after']
 print(backup);print('Verified',len(inventory),'files')
