import json,subprocess,time,sys
from pathlib import Path
repo=Path(__file__).resolve().parents[2]
runner=['python',str(repo/'audit/2026-10-16-lucide-bar/session-command.py')]
def cmd(*args): return subprocess.check_output(runner+list(args),text=True)
def ipc(action): return cmd('quickshell','-c','apx','ipc','call','host',action)
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
home=Path('/var/lib/apx/environments')/state['name']/'home/apx'
kind=sys.argv[1] if len(sys.argv)>1 else 'airplane'
status=json.loads(ipc('popupStatus'))
if status['visible']:
 cmd('hyprctl','eval','hl.dispatch(hl.dsp.send_shortcut({mods="",key="Escape"}))');time.sleep(.5)
ipc('openKeyboardControls' if kind=='keyboard' else 'openAirplaneControls')
for attempt in range(20):
 time.sleep(.3)
 raw=ipc('popupStatus')
 if not raw.strip():continue
 status=json.loads(raw)
 if status['visible'] and status['displayed_controls']['controlsActivityKind']==kind and not status['animation_running'] and not status['page_transition']:break
else:raise RuntimeError('Airplane page did not settle')
target='/home/apx/.cache/apx-airplane-details.png'
cmd('grim','-g',f"{round(status['visual_x'])},{round(status['panel_y'])} {round(status['visual_width'])}x{round(status['settled_height'])}",target)
(repo/('audit/2026-10-20-control-details/'+kind+'.png')).write_bytes((home/'.cache/apx-airplane-details.png').read_bytes())
(home/'.cache/apx-airplane-details.png').unlink()
(repo/('audit/2026-10-20-control-details/'+kind+'-live-status.json')).write_text(json.dumps(status,indent=2)+'\n')
print('Live airplane menu captured without toggling radios')
