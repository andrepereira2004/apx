#!/usr/bin/env python3
"""Apply minimal Wi-Fi layout to the fixed pilot with backups."""
from pathlib import Path
import datetime,fcntl,hashlib,importlib.util,json,os,re,shutil,sys,time
REPO=Path(__file__).resolve().parents[2]
AUDIT=REPO/'audit/2026-10-20-controls-followup'
SOURCE=REPO/'config/environment-shell-v1'
SEED=Path('/usr/share/apx/config-seeds/environment-shell-v1')
class transform:
 RELATIVES = ['local/bin/apx-microphone-activity-v1', 'quickshell/apx/DesktopActivity.qml', 'quickshell/apx/Appearance.qml', 'local/bin/apx-desktop-activity-v1', 'quickshell/apx/icons/lucide/leaf.svg', 'quickshell/apx/icons/lucide/scale.svg', 'quickshell/apx/icons/lucide/cross.svg', 'quickshell/apx/icons/lucide/gpu.svg', 'quickshell/apx/MediaIsland.qml', 'quickshell/apx/shell.qml', 'quickshell/apx/ControlTile.qml', 'quickshell/apx/MenuHover.qml', 'quickshell/apx/BarButton.qml', 'quickshell/apx/BounceMouseArea.qml', 'quickshell/apx/PersonalizationPanel.qml', 'quickshell/apx/RadioIconButton.qml', 'quickshell/apx/qmldir', 'local/bin/apx-install-v1', 'local/bin/apx-pointer-power-v1', 'quickshell/apx/icons/lucide/list.svg', 'quickshell/apx/icons/lucide/mouse-off.svg']
 RELATIVES += ['quickshell/apx/icons/lucide/camera-off.svg', 'quickshell/apx/icons/lucide/plane-off.svg']
 RELATIVES += ['hypr/hyprland.lua', 'hyprland/hyprland.conf']
 RELATIVES += ['quickshell/apx/'+name for name in ['ActivityPanel.qml', 'ControlDashboard.qml', 'IconLabel.qml', 'MediaTimeline.qml', 'WorkspacePreview.qml']]
 RELATIVES += ['quickshell/apx/ControlIcon.qml', 'quickshell/apx/ButtonOutline.qml', 'local/libexec/apx-rofi-secondary-v1.so']
 @staticmethod
 def transform(rel, text): return (SOURCE/rel).read_text()
def atomic(path,data,mode,uid,gid):
 assert not path.is_symlink(),path
 temp=path.with_name(path.name+'.control-centre-tmp');temp.write_bytes(data);os.chmod(temp,mode);os.chown(temp,uid,gid);os.replace(temp,path)
def main():
 assert Path('/etc/hostname').read_text().strip()=='apx-host'
 assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
 assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
 homes=[d/'home/apx' for d in sorted(Path('/var/lib/apx/environments').iterdir())
        if (d/'registration.json').is_file() and (d/'home/apx/.config/quickshell/apx/shell.qml').is_file()]
 if len(sys.argv)==3 and sys.argv[1]=='--rollback':
  backup=Path(sys.argv[2]).resolve();assert backup.parent==Path('/var/lib/apx/backups') and backup.name.endswith('-controls-followup')
  for item in json.loads((backup/'inventory.json').read_text()):
   if item.get('existed',True):atomic(Path(item['path']),(backup/item['path'].lstrip('/')).read_bytes(),item['mode'],item['uid'],item['gid'])
   elif Path(item['path']).exists():Path(item['path']).unlink()
  for home in homes:(home/'.config/quickshell/apx/shell.qml').touch()
  print('Restored',backup);return
 assert sys.argv[1:] in ([],['--check'])
 planned={}
 for base in [SOURCE,SEED]+homes:
  for rel in transform.RELATIVES:
   path=base/rel if base in [SOURCE,SEED] else (base/'.local'/rel.removeprefix('local/') if rel.startswith('local/') else base/'.config'/rel)
   assert not path.is_symlink(),path
   assert path.is_file() or rel in ('local/share/apx/graphite-apps.css', 'local/share/themes/APX-Graphite/gtk-3.0/gtk.css', 'local/share/applications/xfce4-taskmanager.desktop') or rel == 'local/share/icons/APX-Graphite/scalable/devices/apx-host-terminal.svg' or rel == 'local/lib/rofi/apx-rofi-system-v1.so' or rel in ('local/libexec/apx-thunar-chrome-v1.so', 'local/libexec/apx-rofi-secondary-v1.so') or rel in ('local/share/dbus-1/services/org.xfce.Thunar.service', 'local/share/dbus-1/services/org.xfce.FileManager.service', 'local/share/dbus-1/services/org.xfce.Thunar.FileManager1.service') or rel.startswith('local/share/icons/APX-Graphite/scalable/actions/') or rel == 'hypr/apx-trackpad-sensitivity.lua' or rel in ('quickshell/apx/ButtonOutline.qml', 'quickshell/apx/GhostLines.js') or rel.endswith(('RadioIconButton.qml', 'MenuHover.qml', 'CameraIndicator.qml', 'NotificationInbox.qml', 'NotificationGroups.js')) or rel.startswith('local/bin/') or rel.endswith(('mouse-pointer-2.svg', 'arrow-up-down.svg', 'list.svg', 'mouse-off.svg', 'leaf.svg', 'scale.svg', 'cross.svg', 'gpu.svg', 'camera-off.svg', 'plane-off.svg')),path
   planned[path]=(SOURCE/rel).read_bytes() if rel.endswith('.so') else (transform.transform_path(rel,path.read_text() if path.exists() else '',path) if hasattr(transform,'transform_path') else transform.transform(rel,path.read_text() if path.exists() else '')).encode()
 for runtime,base in [(REPO/'scripts/virtual-lab/apx-lab-runtime.py',SOURCE),(Path('/usr/lib/apx/apx-lab-runtime.py'),SEED)]:
  text=runtime.read_text()
  if base == SEED:
   source=(REPO/'scripts/virtual-lab/apx-lab-runtime.py').read_text()
   block=source[source.index('# Pacman runs this after desktop-entry changes'):source.index('def copy_environment_shell_seed(')]
   if 'def configure_environment_application_hook(' not in text:
    text=text.replace('def copy_environment_shell_seed(',block+'def copy_environment_shell_seed(',1)
    text=text.replace('            copy_environment_shell_seed(ENVIRONMENT_SHELL_SEED, user_home)','            copy_environment_shell_seed(ENVIRONMENT_SHELL_SEED, user_home)\n            configure_environment_application_hook(root)',1)
  start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2;section=text[start:end]
  for rel in transform.RELATIVES:
   digest=hashlib.sha256(planned[base/rel]).hexdigest()
   section,n=re.subn(r'("'+re.escape(rel)+r'": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest+m[2],section);assert n<=1,rel
   if not n:section=section.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    '+json.dumps(rel)+': '+json.dumps(digest)+',',1)
  planned[runtime]=(text[:start]+section+text[end:]).encode()
 for home in homes:
  target=home.parent.parent/'root/etc/pacman.d/hooks/99-apx-application-catalog.hook'
  assert target.parent.is_dir() and not target.is_symlink(), target
  data=(REPO/'config/environment-package-install-v1/99-apx-application-catalog.hook').read_bytes()
  assert not target.exists() or target.read_bytes()==data, target
  planned[target]=data
 recovery=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
 text,n=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+hashlib.sha256(planned[REPO/'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(),recovery.read_text());assert n==1
 planned[recovery]=text.encode();planned={p:d for p,d in planned.items() if not p.exists() or p.read_bytes()!=d}
 if sys.argv[1:]==['--check']:
  (AUDIT/'planned-paths.json').write_text(json.dumps([str(p) for p in planned],indent=2)+'\n')
  for rel in transform.RELATIVES:
   dest=AUDIT/'candidate'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((SOURCE/rel).read_bytes() if rel.endswith('.so') else transform.transform(rel,(SOURCE/rel).read_text() if (SOURCE/rel).exists() else '').encode())
  print('Planned',len(planned),'files');return
 if not planned:print('OSD geometry already updated.');return
 backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-controls-followup');backup.mkdir(parents=True)
 inventory=[]
 for path,data in planned.items():
  existed=path.exists();stat=path.stat() if existed else path.parent.stat();saved=backup/str(path).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True)
  if existed:shutil.copy2(path,saved)
  inventory.append(dict(path=str(path),existed=existed,mode=stat.st_mode&0o777 if existed else (0o755 if '/bin/' in str(path) else 0o644),uid=stat.st_uid,gid=stat.st_gid,before=hashlib.sha256(path.read_bytes()).hexdigest() if existed else None,after=hashlib.sha256(data).hexdigest()))
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
