from pathlib import Path
import ast,hashlib,json,re,subprocess,time
repo=Path(__file__).resolve().parents[2];session=repo/'audit/2026-10-16-lucide-bar/session-command.py'
results={}
def run(*args):return subprocess.run(['python',str(session),*args],check=True,capture_output=True,text=True).stdout
for label,action,kind in [('wifi','openWifiControls','controls'),('bluetooth','openBluetoothControls','controls'),('volume','openVolumeControls','controls'),('calendar','openCalendar','calendar'),('environments','openEnvironments','environments'),('battery','toggleBattery','battery')]:
 run('quickshell','-c','apx','ipc','call','host',action);time.sleep(.25)
 state=json.loads(run('quickshell','-c','apx','ipc','call','host','popupStatus'))
 assert state['visible'] and state['kind']==kind,(label,state)
 assert not state['animation_pending'] and not state['animation_running'],(label,state)
 results[label]=state
 run('grim','/home/apx/.cache/apx-lucide-'+label+'.png')
 source=Path('/var/lib/apx/environments/minecraft/home/apx/.cache')/('apx-lucide-'+label+'.png')
 (session.parent/(label+'.png')).write_bytes(source.read_bytes())
run('quickshell','-c','apx','ipc','call','host','toggleBattery')
for file,root in [(repo/'scripts/virtual-lab/apx-lab-runtime.py',repo/'config/environment-shell-v1'),(Path('/usr/lib/apx/apx-lab-runtime.py'),Path('/usr/share/apx/config-seeds/environment-shell-v1'))]:
 tree=ast.parse(file.read_text());assets=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ENVIRONMENT_SHELL_ASSETS' for t in n.targets))
 # Validate every changed/new icon, font, and QML file against the pinned map.
 selected={k:v for k,v in assets.items() if k.startswith(('quickshell/apx/icons/lucide/','local/share/fonts/jetbrains-mono/')) or k in ['quickshell/apx/shell.qml','quickshell/apx/WorkspaceStrip.qml','quickshell/apx/BarButton.qml','quickshell/apx/IconLabel.qml','quickshell/apx/LucideIcon.qml']}
 for rel,digest in selected.items():assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==digest,rel
 results[str(root)]={'pinned_assets_verified':len(selected)}
for name in ['hub','faculdade','hytale','minecraft','steam']:
 home=Path('/var/lib/apx/environments')/name/'home/apx'
 shell=(home/'.config/quickshell/apx/shell.qml').read_text()
 for required in ['readonly property string batteryIconName','iconName: "hexagon"','alternateIconName: "ghost"','iconName: root.appsIconName','label: root.environmentLabel','iconName: "monitor"']:assert required in shell,(name,required)
 for rel in ['BarButton.qml','LucideIcon.qml','IconLabel.qml']:
  assert (home/'.config/quickshell/apx'/rel).read_bytes()==(repo/'config/environment-shell-v1/quickshell/apx'/rel).read_bytes()
 results[name]='installed bar and components verified'
(session.parent/'verification.json').write_text(json.dumps(results,indent=2)+'\n')
print('Six live menus verified; source/installed digests and five Environment copies match.')
