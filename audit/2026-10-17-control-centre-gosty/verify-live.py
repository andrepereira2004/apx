import subprocess,json,time
from pathlib import Path
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent
runner=['python',str(r/'audit/2026-10-16-lucide-bar/session-command.py')]
def cmd(*args):return subprocess.check_output(runner+list(args),text=True)
def ipc(action):return cmd('quickshell','-c','apx','ipc','call','host',action)
def status():return json.loads(ipc('popupStatus'))
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());h=Path('/var/lib/apx/environments')/state['name']/'home/apx'
def capture(name,bar=False):
 s=status();x=round(s['visual_x']);y=round(s['panel_y']);w=round(s['visual_width']);height=round(s['visual_height'])
 geometry='500,0 780x46' if bar else f'{x},{y} {w}x{height}'
 cmd('grim','-g',geometry,'/home/apx/.cache/apx-gosty-verify.png')
 p=h/'.cache/apx-gosty-verify.png';(a/name).write_bytes(p.read_bytes());p.unlink()
results={}
initial=status()
if initial['visible']:ipc('toggleControls');time.sleep(.5)
ipc('openControls');start=time.monotonic();time.sleep(.7)
s=status();assert s['ghost_visible'] and s['ghost_width']>0,s
results['greeting']=s;capture('bar-greeting.png',True);capture('dashboard.png')
ipc('openConnectivityControls');time.sleep(.6)
s=status();assert s['displayed_controls']['controlsConnectivityOpen'],s
results['connectivity']=s;capture('connectivity.png')
ipc('openWifiControls');time.sleep(.5)
s=status();assert s['displayed_controls']['controlsWifiOpen'] and not s['displayed_controls']['controlsConnectivityOpen'],s
results['wifi_navigation']=True
ipc('openBluetoothControls');time.sleep(.5)
s=status();assert s['displayed_controls']['controlsBluetoothOpen'],s
results['bluetooth_navigation']=True
ipc('openControls');time.sleep(.5)
# Direct submenu navigation does not extend the greeting lifetime.
while time.monotonic()-start<10.5:time.sleep(.2)
s=status();assert not s['ghost_visible'] and s['ghost_width']<1,s
results['expired']=s;capture('bar-restored.png',True)
ipc('toggleControls')
results['configerrors']=cmd('hyprctl','configerrors').strip();assert not results['configerrors']
(a/'live-results.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS: 10-second greeting, restored bar, grouped connections, Wi-Fi/Bluetooth navigation, clean compositor configuration')
