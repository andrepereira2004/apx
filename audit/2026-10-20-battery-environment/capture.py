import json,subprocess,time
from pathlib import Path
repo=Path(__file__).resolve().parents[2];out=Path(__file__).parent
runner=['python',str(repo/'audit/2026-10-16-lucide-bar/session-command.py')]
def cmd(*args):return subprocess.check_output(runner+list(args),text=True)
def ipc(action):return cmd('quickshell','-c','apx','ipc','call','host',action)
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());home=Path('/var/lib/apx/environments')/state['name']/'home/apx';results={}
for action,kind in [('toggleBattery','battery'),('openEnvironments','environments')]:
 raw=ipc('popupStatus')
 if raw.strip() and json.loads(raw)['visible']:
  cmd('hyprctl','eval','hl.dispatch(hl.dsp.send_shortcut({mods="",key="Escape"}))');time.sleep(.5)
 ipc(action)
 for i in range(25):
  time.sleep(.2);raw=ipc('popupStatus')
  if not raw.strip():continue
  status=json.loads(raw)
  if status['visible'] and status['kind']==kind and not status['animation_running']:break
 else:raise RuntimeError('Unsettled '+kind)
 time.sleep(.5);status=json.loads(ipc('popupStatus'))
 target='/home/apx/.cache/apx-battery-environment.png'
 cmd('grim','-g',f"{round(status['visual_x'])},{round(status['panel_y'])} {round(status['visual_width'])}x{round(status['settled_height'])}",target)
 (out/(kind+'.png')).write_bytes((home/'.cache/apx-battery-environment.png').read_bytes());(home/'.cache/apx-battery-environment.png').unlink();results[kind]=status
(out/'live-status.json').write_text(json.dumps(results,indent=2)+'\n');print('Battery and workload Environment captured; no power/lifecycle actions')
