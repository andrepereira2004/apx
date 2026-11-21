from pathlib import Path
import datetime,hashlib,json,fcntl,os,re,shutil,stat
repo=Path(__file__).resolve().parents[2]
assert Path('/etc/hostname').read_text().strip()=='apx-host'
assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
source=repo/'config/environment-shell-v1/quickshell/apx/shell.qml'
# Apply only these reviewed changes to each independent installed shell.
def transform(text):
 changes=[
 ('        powerTransitionActive = action === "reboot" || action === "poweroff"','        powerTransitionActive = false'),
 ('if (root.powerAction !== "suspend" || root.idleSuspendRequested) root.confirmPower()','if (root.powerAction === "suspend" && root.idleSuspendRequested) root.confirmPower()'),
 ('            powerMessage = "A fechar o Environment de forma segura..."','            powerTransitionActive = powerAction === "reboot" || powerAction === "poweroff"\n            powerMessage = "A fechar o Environment de forma segura..."'),
 ('height: visible ? 104 : 0\n                        radius: 7\n                        color: root.controlButtonSurface\n                        border.width: 1\n                        border.color: root.powerToken.length','height: visible ? powerConfirmationContent.implicitHeight + 18 : 0\n                        radius: 7\n                        color: root.controlButtonSurface\n                        border.width: 1\n                        border.color: root.powerToken.length'),
 ('border.color: root.powerToken.length ? "#ffb15a" : root.controlButtonOutline\n                        Column {','border.color: root.powerToken.length ? "#ffb15a" : root.controlButtonOutline\n                        Column {\n                            id: powerConfirmationContent'),
 ('label: root.powerBusy ? "A processar..." : "Confirmar"\n                                    accent: true\n                                    onActivated: root.confirmPower()','label: root.powerBusy ? "A processar..." : root.powerAction === "reboot" ? "Reiniciar" : root.powerAction === "poweroff" ? "Desligar" : "Suspender"\n                                    enabled: !root.powerBusy\n                                    accent: true\n                                    onActivated: root.confirmPower()')]
 for before,after in changes:
  assert text.count(before)==1,before
  text=text.replace(before,after,1)
 return text.encode()
seed=Path('/usr/share/apx/config-seeds/environment-shell-v1/quickshell/apx/shell.qml')
targets=[seed]+[p/'home/apx/.config/quickshell/apx/shell.qml' for p in Path('/var/lib/apx/environments').iterdir() if (p/'registration.json').is_file()]
planned={p:transform(p.read_text()) for p in targets}
digest=lambda data:hashlib.sha256(data).hexdigest()
for runtime,asset in ((repo/'scripts/virtual-lab/apx-lab-runtime.py',source.read_bytes()),(Path('/usr/lib/apx/apx-lab-runtime.py'),planned[seed])):
 text,count=re.subn(r'("quickshell/apx/shell.qml": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest(asset)+m[2],runtime.read_text());assert count==1
 planned[runtime]=text.encode()
p=repo/'scripts/physical-pilot/recover-development-quota-v1.sh'
text,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+digest(planned[repo/'scripts/virtual-lab/apx-lab-runtime.py']),p.read_text());assert count==1
planned[p]=text.encode()
with open('/run/apx/machine-transition-v1.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-power-confirmation');backup.mkdir(mode=0o700)
 inventory=[]
 for target,data in planned.items():
  meta=target.stat();assert not target.is_symlink()
  saved=backup/target.relative_to('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
  inventory.append(dict(path=str(target),before=digest(target.read_bytes()),after=digest(data),uid=meta.st_uid,gid=meta.st_gid,mode=stat.S_IMODE(meta.st_mode)))
 (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
 for entry in inventory:
  target=Path(entry['path']);temporary=target.with_name(target.name+'.power-new');temporary.write_bytes(planned[target]);os.chmod(temporary,entry['mode']);os.chown(temporary,entry['uid'],entry['gid']);os.replace(temporary,target)
  assert digest(target.read_bytes())==entry['after']
 print(backup);print('Verified',len(inventory),'files')
